# Free-Tier Global Edge CDN via Cloudflare

Since you require this to stay within the **free tier**, using AWS CloudFront or S3 for video hosting is not viable (they charge heavily for outbound bandwidth).

However, **Cloudflare** offers an incredibly generous free tier that includes unlimited CDN bandwidth and edge caching. 

Here is the exact architecture to make your platform globally fast for free:

## Architecture
1. **Origin Server**: Your application runs on Render, DigitalOcean, or an on-premise server. Your `media_data` volume stores the `.ts` and `.m3u8` video chunks.
2. **Cloudflare Proxy**: You point your domain's nameservers to Cloudflare.
3. **Cache Rules**: We configure Cloudflare to heavily cache the immutable `.ts` video chunks at their edge nodes globally. 

When a user in Tokyo requests a video segment, they download it from the Cloudflare Tokyo datacenter, meaning your origin server pays **0 bandwidth costs** and the user experiences 0ms buffering.

---

## Step 1: Nginx Configuration Upgrade
First, we must configure your origin Nginx server to add the correct `Cache-Control` headers. Cloudflare respects these headers and caches the files automatically.

The `.ts` files are immutable (they never change once transcoded), so we cache them for 1 year. The `.m3u8` playlists might change, so we don't cache them.

## Step 2: Cloudflare Page Rules setup
Once your domain (e.g. `flick.com`) is using Cloudflare nameservers, you need to configure a Page Rule in the Cloudflare Dashboard to enforce the caching of your video chunks (which can sometimes be bypassed by default settings).

1. Go to your Cloudflare Dashboard -> **Rules** -> **Page Rules**.
2. Click **Create Page Rule**.
3. **URL Pattern:** `*flick.com/api/streaming/hls/*/*.ts` 
4. **Settings:**
    - `Cache Level` = **Cache Everything**
    - `Edge Cache TTL` = **a year**
5. Click **Save and Deploy**.

## Result 🚀
With just these two steps (Nginx headers + Cloudflare rule), your streaming platform is now **globally distributed for free**.
If 100,000 users try to watch "Inception" at the exact same time:
- The very first user will trigger a request to your origin server (fetching the `.ts` chunk).
- Your origin server will respond with the chunk and the `Cache-Control: public, max-age=31536000` header.
- Cloudflare will intercept this chunk, save a copy in all 300+ of its global data centers.
- The remaining 99,999 users will download the chunk directly from Cloudflare. Your server won't even notice the traffic spike!
