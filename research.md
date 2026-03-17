# Using Claude AI to manage YouTube: a complete technical guide

**Claude can absolutely automate YouTube channel management today, but there's no official turnkey solution — you'll assemble it from powerful building blocks.** The YouTube Data API v3 supports nearly every channel management action (updating titles, descriptions, tags, thumbnails, playlists, even uploading and deleting videos), while separate Analytics and Reporting APIs deliver performance data. Anthropic offers no official YouTube MCP server, but a thriving ecosystem of **69+ community-built MCP servers** fills the gap, with one standout project — `eat-pray-ai/yutu` — providing full read-write YouTube control through Claude. The practical path forward combines Google's APIs, a community MCP server, and Claude Code's agent capabilities.

---

## The YouTube Data API v3 covers almost everything a creator needs

The Data API v3 is remarkably comprehensive for channel management. Every operation a content creator would want to automate through Claude is supported, with one major class of exceptions.

**What you CAN do programmatically:**

| Operation | API Method | Quota Cost |
|-----------|-----------|------------|
| Update video titles, descriptions, tags | `videos.update` (PUT) | 50 units |
| Set custom thumbnails | `thumbnails.set` (POST) | 50 units |
| Create/update/delete playlists | `playlists.insert/update/delete` | 50 units |
| Add/remove videos from playlists | `playlistItems.insert/delete` | 50 units |
| Upload videos | `videos.insert` (POST) | 1,600 units |
| Delete videos | `videos.delete` (DELETE) | 50 units |
| Manage comments | `comments.insert/update/delete` | 50 units |
| Manage captions/subtitles | `captions.insert/update/delete` | Varies |
| Update channel branding | `channels.update` | 50 units |
| Schedule video publishing | `status.publishAt` field | — |

The default daily quota is **10,000 units**, which translates to roughly 6 video uploads or 200 metadata updates per day. Projects needing more must pass Google's compliance audit.

**What you CANNOT do via any YouTube API** — and this matters for optimization workflows:

- **Community Posts**: No API support whatsoever for creating, editing, or reading Community tab posts
- **End screens and info cards**: Cannot be managed programmatically (active feature request on Google's Issue Tracker)
- **Monetization settings**: Cannot enable/disable ads or control ad placements
- **YouTube Shorts-specific features**: No dedicated Shorts endpoints; Shorts upload as regular videos (vertical, ≤3 minutes)
- **Video chapters**: No structured API — chapters derive from timestamps in descriptions, so Claude can generate them as description text
- **Channel name/handle changes**: Must be done manually in YouTube Studio

One critical constraint: **service accounts don't work** with the YouTube Data API. All write operations require interactive OAuth 2.0 user authorization — a real human must authenticate at least once.

## Analytics lives in two separate APIs with different strengths

YouTube analytics data does **not** come from the Data API v3 (which only returns basic counts like views and likes). Instead, Google provides two dedicated analytics APIs.

The **YouTube Analytics API** handles real-time targeted queries. You request specific metrics (views, watch time, impressions, CTR, subscriber changes, estimated revenue) sliced by dimensions like date, country, device type, traffic source, and demographics. This powers interactive dashboards — ask it "how did my videos perform in Germany last month by device type" and get an immediate response. It supports **impression click-through rate**, which is critical for thumbnail optimization, along with audience retention data per video.

The **YouTube Reporting API** takes a fundamentally different approach: you schedule reporting jobs, and YouTube generates daily CSV bulk downloads covering 24-hour periods. It includes data unavailable in the Analytics API, such as subtitle metrics, playlist audience retention, and (for content owners) actual ad revenue rather than estimates. The tradeoff is latency — reports aren't instant but are ideal for data warehousing and trend analysis.

For a creator using Claude to optimize their channel, the Analytics API is the right starting point. It delivers the metrics that drive optimization decisions: **impressions, CTR, average view duration, traffic sources, and audience demographics** — all queryable in real time.

## OAuth scopes map cleanly to channel management tasks

Claude (or any tool acting on a creator's behalf) needs the right OAuth 2.0 scopes. Here's the practical mapping:

| Task | Required Scope |
|------|---------------|
| Read channel/video data | `youtube.readonly` |
| Update metadata, thumbnails, playlists | `youtube` or `youtube.force-ssl` |
| Upload videos | `youtube.upload` |
| Delete videos and manage comments | `youtube.force-ssl` |
| View analytics (views, engagement, retention) | `yt-analytics.readonly` |
| View revenue/ad analytics | `yt-analytics-monetary.readonly` |

For a full channel management setup, a creator would authorize four scopes: **`youtube.force-ssl`** (covers all read/write operations including deletion), **`youtube.upload`** (for video uploads), **`yt-analytics.readonly`** (engagement metrics), and **`yt-analytics-monetary.readonly`** (revenue data). The `youtube.force-ssl` scope is functionally equivalent to the broader `youtube` scope but enforces SSL — Google recommends it for all new projects.

## No official YouTube MCP server exists, but the community delivers

Anthropic maintains **seven reference MCP servers** (Filesystem, Git, Fetch, Memory, Sequential Thinking, Time, Everything) and lists hundreds of official third-party integrations from companies like Atlassian, AWS, and Cloudflare. **YouTube is not among any of these.** There is no official Anthropic documentation, SDK, or example for YouTube integration. Google has not published an official YouTube MCP server either.

However, the community ecosystem is remarkably active. PulseMCP tracks **69+ YouTube MCP servers**, and several have reached production quality. The landscape breaks down into clear tiers:

**`eat-pray-ai/yutu`** (~400 stars, Go, Apache-2.0) is the only major MCP server with **full read AND write** capabilities. Updated as recently as March 2026, it operates as both a CLI tool and MCP server, using OAuth 2.0 for user-level authentication. It supports video uploads, metadata updates, playlist management, comment posting, and even channel membership listing. For a creator wanting Claude to actually *manage* their channel — not just read data — **yutu is the clear choice today**.

**`ZubeidHendricks/youtube-mcp-server`** (~453 stars, TypeScript) is the most comprehensive read-only option, exposing video details, channel stats, playlist data, transcripts, and search through a clean npm package. It includes a `CLAUDE.md` file specifically for Claude Code integration.

**`kimtaeyoon83/mcp-server-youtube-transcript`** (~490 stars, TypeScript) dominates the transcript-extraction niche — zero dependencies, multi-language support, ad/sponsorship filtering. Ideal for competitive research and content analysis but doesn't touch the Data API.

For analytics specifically, **Windsor.ai** offers a polished commercial solution (free tier available, paid from $19/month) that pipes YouTube Analytics data directly into Claude via MCP, covering watch time, subscriber changes, impressions, CTR, and estimated revenue across multiple channels.

## GitHub projects already combine Claude with YouTube workflows

Several open-source projects demonstrate the Claude + YouTube combination in practice:

**`wnstify/tubeflow`** is the most ambitious: a "research-first YouTube content creation system" built natively for Claude Code. It deploys five specialized AI agents in parallel for topic analysis, competitor research, SEO intelligence, community insights, and strategic synthesis, then drives an end-to-end workflow from research through creation, review, and publishing. It claims to compress a 4-hour content creation process to 30 minutes.

**`AgriciDaniel/claude-seo`** provides a universal SEO skill for Claude Code with 13 sub-skills and 7 subagents, including VideoObject schema markup for YouTube — useful for optimizing video discoverability in search engines beyond YouTube itself.

A well-documented **DEV Community project** demonstrates a complete automation pipeline: RSS news feeds → Claude API for script generation → text-to-speech → FFmpeg rendering → YouTube Data API upload, producing 4 automated Shorts per day with 120+ videos created. The stack uses Node.js, `claude-3-5-sonnet`, and the YouTube Data API v3.

Workflow automation platforms also bridge the gap: **n8n** and **Zapier** both offer pre-built templates connecting YouTube triggers (new video, new comment, analytics thresholds) with Claude actions (generate descriptions, analyze performance, suggest optimizations). **Composio** provides a managed MCP platform that handles OAuth token refresh and exposes YouTube operations alongside 850+ other services.

## The practical architecture for Claude-powered YouTube optimization

A creator wanting to build this today should combine three layers. First, **install `yutu`** as an MCP server in Claude Code or Claude Desktop — this gives Claude direct read-write access to the YouTube Data API through OAuth. Second, **connect analytics** either through the Analytics API directly (via a custom script or the Windsor.ai MCP connector) to feed Claude performance data. Third, **add a content strategy layer** like TubeFlow's Claude Code skills or custom `CLAUDE.md` instructions that encode the creator's brand voice, content strategy, and optimization goals.

The resulting system can analyze which videos underperform on CTR (suggesting thumbnail and title changes), identify content gaps from competitor analysis, bulk-update descriptions with optimized keywords, manage playlist organization, generate SEO-optimized metadata for new uploads, and even draft scripts — all orchestrated through natural language conversations with Claude.

## What remains genuinely difficult

Three constraints limit what's possible today. **Quota limits** cap throughput at roughly 200 write operations per day without an approved increase — fine for most individual creators but restrictive for agencies managing dozens of channels. **The OAuth requirement** means initial setup requires manual browser-based authentication; Claude cannot autonomously obtain access tokens without a human approving the consent screen at least once (though tokens can be refreshed automatically afterward). And **the community MCP servers carry no official support** — they're volunteer-maintained, unaudited by Anthropic, and could break with YouTube API changes. The `yutu` project's active maintenance and Apache-2.0 license mitigate this risk, but creators should understand they're building on community infrastructure rather than enterprise-supported tooling.

Despite these caveats, the technical foundation is solid. The YouTube APIs are mature and well-documented, the MCP ecosystem is rapidly maturing, and Claude Code's agent architecture is purpose-built for exactly this kind of multi-tool orchestration. A technically comfortable creator can have a working Claude-powered YouTube optimization system running within an afternoon.