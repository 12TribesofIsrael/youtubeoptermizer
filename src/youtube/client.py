"""YouTube API client wrapper for channel management."""

from .auth import get_authenticated_service
from googleapiclient.http import MediaFileUpload


class YouTubeClient:
    def __init__(self):
        self.youtube = get_authenticated_service("youtube", "v3")
        self.analytics = get_authenticated_service("youtubeAnalytics", "v2")
        self._channel_id = None

    @property
    def channel_id(self):
        if not self._channel_id:
            resp = self.youtube.channels().list(part="id", mine=True).execute()
            self._channel_id = resp["items"][0]["id"]
        return self._channel_id

    # ── Videos ──────────────────────────────────────────────

    def list_videos(self, max_results=50):
        """Fetch all channel videos with metadata. Returns list of video dicts."""
        videos = []
        request = self.youtube.search().list(
            part="snippet",
            channelId=self.channel_id,
            maxResults=min(max_results, 50),
            order="date",
            type="video",
        )
        while request and len(videos) < max_results:
            response = request.execute()
            video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
            if video_ids:
                details = (
                    self.youtube.videos()
                    .list(
                        part="snippet,statistics,contentDetails,status",
                        id=",".join(video_ids),
                    )
                    .execute()
                )
                videos.extend(details.get("items", []))
            request = self.youtube.search().list_next(request, response)
        return videos[:max_results]

    def get_video(self, video_id):
        """Get full details for a single video."""
        resp = (
            self.youtube.videos()
            .list(part="snippet,statistics,contentDetails,status", id=video_id)
            .execute()
        )
        items = resp.get("items", [])
        return items[0] if items else None

    def update_video(self, video_id, title=None, description=None, tags=None, category_id=None):
        """Update video metadata. Only provided fields are changed."""
        video = self.get_video(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        snippet = video["snippet"]
        if title is not None:
            snippet["title"] = title
        if description is not None:
            snippet["description"] = description
        if tags is not None:
            snippet["tags"] = tags
        if category_id is not None:
            snippet["categoryId"] = category_id

        return (
            self.youtube.videos()
            .update(
                part="snippet",
                body={"id": video_id, "snippet": snippet},
            )
            .execute()
        )

    def delete_video(self, video_id):
        """Permanently delete a video. Use with caution."""
        return self.youtube.videos().delete(id=video_id).execute()

    def set_thumbnail(self, video_id, image_path):
        """Upload a custom thumbnail for a video."""
        media = MediaFileUpload(image_path, mimetype="image/jpeg")
        return (
            self.youtube.thumbnails()
            .set(videoId=video_id, media_body=media)
            .execute()
        )

    # ── Playlists ───────────────────────────────────────────

    def list_playlists(self):
        """List all playlists on the channel."""
        playlists = []
        request = self.youtube.playlists().list(
            part="snippet,contentDetails", mine=True, maxResults=50
        )
        while request:
            response = request.execute()
            playlists.extend(response.get("items", []))
            request = self.youtube.playlists().list_next(request, response)
        return playlists

    def create_playlist(self, title, description="", privacy="public"):
        """Create a new playlist."""
        return (
            self.youtube.playlists()
            .insert(
                part="snippet,status",
                body={
                    "snippet": {"title": title, "description": description},
                    "status": {"privacyStatus": privacy},
                },
            )
            .execute()
        )

    def add_to_playlist(self, playlist_id, video_id):
        """Add a video to a playlist."""
        return (
            self.youtube.playlistItems()
            .insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id,
                        },
                    }
                },
            )
            .execute()
        )

    def remove_from_playlist(self, playlist_item_id):
        """Remove a video from a playlist by playlist item ID."""
        return self.youtube.playlistItems().delete(id=playlist_item_id).execute()

    # ── Analytics ───────────────────────────────────────────

    def get_analytics(self, start_date, end_date, video_id=None):
        """Pull analytics metrics for a date range. Optionally filter by video."""
        params = {
            "ids": f"channel=={self.channel_id}",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,likes,comments",
            "dimensions": "video" if not video_id else "day",
            "sort": "-views",
            "maxResults": 50,
        }
        if video_id:
            params["filters"] = f"video=={video_id}"
            params["dimensions"] = "day"

        return self.analytics.reports().query(**params).execute()

    def get_video_impressions(self, start_date, end_date, video_id=None):
        """Pull impression and CTR data."""
        params = {
            "ids": f"channel=={self.channel_id}",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "views,impressions,impressionClickThroughRate,averageViewDuration",
            "dimensions": "video",
            "sort": "-impressions",
            "maxResults": 50,
        }
        if video_id:
            params["filters"] = f"video=={video_id}"
        return self.analytics.reports().query(**params).execute()

    # ── Channel Info ────────────────────────────────────────

    def get_channel_info(self):
        """Get channel name, subscriber count, video count."""
        resp = (
            self.youtube.channels()
            .list(part="snippet,statistics", mine=True)
            .execute()
        )
        return resp["items"][0] if resp.get("items") else None

    def get_branding_settings(self):
        """Fetch current channel brandingSettings (About description, keywords, etc)."""
        resp = (
            self.youtube.channels()
            .list(part="brandingSettings", mine=True)
            .execute()
        )
        return resp["items"][0] if resp.get("items") else None

    def update_channel_description(self, description):
        """Replace the About-page description. Preserves other brandingSettings fields."""
        current = self.get_branding_settings()
        if not current:
            raise ValueError("Could not fetch current brandingSettings")
        branding = current["brandingSettings"]
        branding.setdefault("channel", {})["description"] = description
        return (
            self.youtube.channels()
            .update(
                part="brandingSettings",
                body={"id": current["id"], "brandingSettings": branding},
            )
            .execute()
        )
