// www.ceotalks.online 跳到 ceotalks.online，其余照常给静态文件
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www.ceotalks.online") {
      url.hostname = "ceotalks.online";
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
