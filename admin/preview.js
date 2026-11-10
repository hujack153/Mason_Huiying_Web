/* 後台即時預覽：用網站本身的 CSS，照網站的 HTML 結構組出文章與產品的樣子。
 * 對應產生器：_build/build_all3.py（文章）、build_all.py（系列 series_rows）、build_all2.py（仿石）。
 */
(function () {
  if (!window.CMS) return;
  CMS.registerPreviewStyle("/assets/css/site.css");
  CMS.registerPreviewStyle(
    "body{background:#fff}.pv-note{font:12px/1.5 system-ui,sans-serif;color:#8a877f;" +
    "padding:10px 24px;border-bottom:1px solid #e6e3dc;background:#faf9f6}" +
    ".acc .rb{display:block!important}", { raw: true });

  var h = window.h;

  // ── 小工具
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  // **粗體** → <b>（與產生器的 content.py 相同規則）
  function md(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>"); }
  function list(v) { return v && v.toJS ? v.toJS() : (v || []); }
  function img(props, path) {
    if (!path) return "";
    var a = props.getAsset(path);
    return a ? a.toString() : path;
  }
  function view(html, note) {
    return h("div", {}, [
      h("div", { className: "pv-note", key: "n" }, note || "預覽：實際排版以發布後的網站為準"),
      h("div", { key: "b", dangerouslySetInnerHTML: { __html: html } }),
    ]);
  }

  // ── 文章、施作部位頁共用的段落（§ 1.0、§ 1.1 …）
  function sections(secs) {
    var out = "";
    list(secs).forEach(function (sec, i) {
      var n = i + 1;
      var ps = (sec.p || []).filter(function (p) { return p && p.trim(); })
        .map(function (p) { return "<p>" + md(p) + "</p>"; }).join("");
      out += '<div class="clause"><div class="s">§ ' + n + '.0</div><div class="b"><h2>' +
        esc(sec.h) + "</h2>" + ps + "</div></div>";
      var li = (sec.list || []).filter(function (x) { return x && x.trim(); });
      if (li.length) {
        out += '<div class="clause note"><div class="s">§ ' + n + '.1</div><div class="b"><ul class="marks">' +
          li.map(function (x) { return "<li>" + md(x) + "</li>"; }).join("") + "</ul></div></div>";
      }
      var t = sec.table || {};
      var rows = (t.rows || []).map(function (r) { return r.cells || []; })
        .filter(function (r) { return r.some(function (c) { return c && c.trim(); }); });
      if (rows.length) {
        out += '<div class="clause"><div class="s">§ ' + n + '.1</div><div class="b"><div class="tbl-wrap"><table class="tbl"><tr>' +
          (t.head || []).map(function (c) { return "<th>" + md(c) + "</th>"; }).join("") + "</tr>" +
          rows.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + md(c) + "</td>"; }).join("") + "</tr>"; }).join("") +
          "</table></div></div></div>";
      }
      var lk = sec.link || {};
      if (lk.text && lk.href) {
        out += '<p style="margin:8px 0 24px"><a class="btn line" href="#">' + esc(lk.text) + " →</a></p>";
      }
    });
    return '<div class="doc">' + out + "</div>";
  }

  // ── 技術專欄文章
  var Article = createClass({
    render: function () {
      var d = this.props.entry.get("data");
      var hero = d.get("hero");
      var html =
        '<div class="head"><div class="page"><span class="tag">技術說明</span>' +
        '<h1 style="max-width:26ch">' + esc(d.get("title")) + "</h1>" +
        '<p class="lead num" style="font-size:15px">發表 ' + esc(d.get("date")) + "</p></div></div>" +
        '<section class="band"><div class="text">' +
        '<p class="abstract">' + md(d.get("lead")) + "</p>" +
        (hero ? '<div style="max-width:560px;margin-bottom:44px"><figure class="plate"><img src="' +
          esc(img(this.props, hero)) + '" alt=""></figure></div>' : "") +
        sections(d.get("sections")) + "</div></section>";
      return view(html);
    },
  });

  // ── 施作部位頁
  var Solution = createClass({
    render: function () {
      var d = this.props.entry.get("data");
      var html =
        '<div class="head"><div class="page"><h1>' + esc(d.get("h1")) + "</h1>" +
        '<p class="lead">' + md(d.get("lead")) + "</p></div></div>" +
        '<section class="band"><div class="text">' + sections(d.get("sections")) +
        (d.get("cta") ? '<p class="abstract" style="margin-top:32px">' + md(d.get("cta")) + "</p>" : "") +
        "</div></section>";
      return view(html);
    },
  });

  // ── 產品系列（防水材料、環氧地坪共用；與網站的展開卡片相同）
  function seriesRows(series, labels, isBase) {
    var n = 0;
    return '<div class="schedule">' + list(series).map(function (s) {
      var base = isBase && isBase(s);
      var k = base ? labels.base : String(++n).padStart(2, "0");
      var feat = (s.feat || []).map(function (f) { return "<li>" + md(f) + "</li>"; }).join("");
      var spec = (s.spec || []).map(function (x) {
        return "<div><span>" + esc(x.k) + "</span><b>" + esc(x.v) + "</b></div>";
      }).join("");
      return '<details class="acc" open><summary><span class="k">' + esc(k) + '</span>' +
        '<span class="t"><h3>' + esc(s.name) + '</h3><span class="role">' + esc(s.tagline || s.tag) + "</span></span>" +
        '<span class="tg" aria-hidden="true"></span></summary><div class="rb">' +
        "<p>" + md(s.desc) + "</p>" +
        '<div class="cols"><div><h5>' + labels.feat + '</h5><ul class="marks">' + feat + "</ul></div>" +
        "<div><h5>" + labels.use + '</h5><p class="use">' + md(s.use) + "</p></div>" +
        "<div><h5>" + labels.spec + '</h5><div class="data">' + spec + "</div></div></div></div></details>";
    }).join("") + "</div>";
  }
  var ZH = { feat: "產品特性", use: "適用部位", spec: "參考規格", base: "基礎" };
  var EN = { feat: "Properties", use: "Applications", spec: "Reference data", base: "Base" };

  function Waterproofing(L) {
    return createClass({
      render: function () {
        var s = list(this.props.entry.getIn(["data", "series"])).filter(function (item) { return !item.archived; });
        var cnt = s.length;
        var html = '<section class="band"><div class="page"><div class="cap"><h2>' +
          (L === ZH ? "共 " + cnt + " 個系列" : cnt + " series") + "</h2></div>" +
          seriesRows(s, L) + "</div></section>";
        return view(html, "預覽：系列數量會自動帶入首頁與關於頁");
      },
    });
  }

  function Epoxy(L) {
    return createClass({
      render: function () {
        var d = this.props.entry.get("data");
        var isBase = function (s) { return s.id === "primer" || s.id === "body"; };
        var cnt = list(d.get("series")).filter(function (s) { return !isBase(s); }).length;
        var faq = list(d.get("faq")).map(function (f) {
          return '<details class="acc" open><summary><span class="t"><h3>' + esc(f.q) +
            '</h3></span></summary><div class="rb"><p>' + md(f.a) + "</p></div></details>";
        }).join("");
        var html =
          '<div class="head"><div class="page"><h1>' + esc(d.get("h1")) + '</h1><p class="lead">' +
          md(d.get("lead")) + "</p></div></div>" +
          '<section class="band"><div class="page"><div class="cap"><div class="no">' + esc(d.get("series_kick")) +
          "</div><h2>" + esc(d.get("series_h2")) + "</h2><p>" + md(d.get("series_p")) + "</p></div>" +
          seriesRows(d.get("series"), L, isBase) + "</div></section>" +
          (faq ? '<section class="band grey"><div class="page"><div class="cap"><h2>' + esc(d.get("faq_h2")) +
            '</h2></div><div class="schedule">' + faq + "</div></div></section>" : "");
        return view(html, "預覽：目前系統數 " + cnt + " 套（不含底塗、中塗）。數量變動時請一起改標題與引言");
      },
    });
  }

  function Stone(L) {
    return createClass({
      render: function () {
        var props = this.props, d = props.entry.get("data");
        var prods = list(d.get("products")).map(function (p, i) {
          var feat = (p.feat || []).map(function (f) { return "<li>" + md(f) + "</li>"; }).join("");
          return '<details class="acc" open><summary><span class="k">' + String(i + 1).padStart(2, "0") +
            '</span><span class="t"><h3>' + esc(p.name) + '</h3></span><span class="tg"></span></summary>' +
            '<div class="rb"><p>' + md(p.desc) + '</p><div class="cols"><div><h5>' + L.feat +
            '</h5><ul class="marks">' + feat + '</ul></div><div><h5>' + L.spec + '</h5><div class="data">' +
            "<div><span>" + (L === ZH ? "用量" : "Coverage") + "</span><b>" + esc(p.qty) + "</b></div>" +
            "<div><span>" + (L === ZH ? "包裝" : "Pack") + "</span><b>" + esc(p.pack) + "</b></div>" +
            "</div></div></div></div></details>";
        }).join("");
        var sw = list(d.get("swatches")).map(function (s) {
          return '<button type="button" class="sw"><img src="' + esc(img(props, s.img)) + '" alt=""><span class="nm">' +
            esc(s.name) + "</span></button>";
        }).join("");
        var html =
          '<section class="band"><div class="page"><div class="cap"><h2>' +
          (L === ZH ? "塗層產品" : "Coats") + '</h2></div><div class="schedule">' + prods + "</div></div></section>" +
          '<section class="band"><div class="page"><div class="cap"><h2>' +
          (L === ZH ? "色卡（共 " + list(d.get("swatches")).length + " 組）" : "Colourways") +
          '</h2></div><div class="swgrid">' + sw + "</div></div></section>";
        return view(html, "預覽：增減塗層時，網站上的剖面圖需請工程師更新");
      },
    });
  }

  CMS.registerPreviewTemplate("articles_zh", Article);
  CMS.registerPreviewTemplate("articles_en", Article);
  CMS.registerPreviewTemplate("solutions_zh", Solution);
  CMS.registerPreviewTemplate("solutions_en", Solution);
  CMS.registerPreviewTemplate("waterproofing_zh", Waterproofing(ZH));
  CMS.registerPreviewTemplate("waterproofing_en", Waterproofing(EN));
  CMS.registerPreviewTemplate("epoxy_zh", Epoxy(ZH));
  CMS.registerPreviewTemplate("epoxy_en", Epoxy(EN));
  CMS.registerPreviewTemplate("stone_zh", Stone(ZH));
  CMS.registerPreviewTemplate("stone_en", Stone(EN));
})();
