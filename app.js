// Shop owner's WhatsApp number, international format without "+".
const WA_NUMBER = "995000000000"; // placeholder: replace with the real shop number

const BOUQUETS = [
  {id:"pinkwhite", cat:["love","birthday"], price:120, img:"pinkwhite", tag:"hit",
   ka:["ვარდისფერი ღრუბელი","ვარდები, მატიოლა და ეუსტომა ჰაეროვან შეფუთვაში"],
   en:["Pink Cloud","Roses, stock and lisianthus in airy wrapping"]},
  {id:"peony", cat:["love","wedding"], price:150, img:"hero",
   ka:["პიონისებრი ვარდები","ნაზი ბაღის ვარდები, უხვად და მსუბუქად"],
   en:["Garden Roses","Soft, full-bloom garden roses"]},
  {id:"red", cat:["love"], price:95, img:"redroses",
   ka:["წითელი ბუშ-ვარდები","კლასიკა, რომელიც არასდროს ბერდება"],
   en:["Red Spray Roses","A classic that never gets old"]},
  {id:"peach", cat:["birthday","vase"], price:140, img:"vase", tag:"vase",
   ka:["ატმისფერი ვაზა","ბუკეტი მინის ვაზით, მზადაა საჩუქრად"],
   en:["Peach in a Vase","Arranged in a glass vase, ready to gift"]},
  {id:"sunny", cat:["birthday"], price:130, img:"sunflower",
   ka:["მზიანი დღე","მზესუმზირა, ჰორტენზია და ნარინჯისფერი ვარდები"],
   en:["Sunny Day","Sunflowers, hydrangea and orange roses"]},
  {id:"meadow", cat:["birthday"], price:110, img:"colorful",
   ka:["მინდვრის ზღაპარი","ფერადი, ცოცხალი, ზაფხულის განწყობით"],
   en:["Meadow Tale","Colourful and lively, a taste of summer"]},
  {id:"tulips", cat:["vase","love"], price:85, img:"pinkvase", tag:"vase",
   ka:["ტიტები ვაზაში","15 ვარდისფერი ტიტა მინის ვაზით"],
   en:["Tulips in a Vase","15 pink tulips with a glass vase"]},
  {id:"ember", cat:["birthday","vase"], price:105, img:"redtable", tag:"vase",
   ka:["ცეცხლოვანი","ნარინჯისფერი და წითელი, ქილაში"],
   en:["Ember","Orange and red, in a jar"]},
  {id:"grand", cat:["wedding","love"], price:220, img:"roses", tag:"premium",
   ka:["დიდი ბუკეტი","ბაღის ვარდები, ევკალიპტი და ტყის კენკრა"],
   en:["The Grand","Garden roses, eucalyptus and wild berries"]},
  {id:"white", cat:["wedding"], price:160, img:"white",
   ka:["თეთრი ნაზი","თეთრი და კრემისფერი, ქორწილისთვის"],
   en:["Soft White","White and cream, made for weddings"]},
  {id:"mini", cat:["love","birthday"], price:45, img:"dried",
   ka:["პატარა სიურპრიზი","მინი ბუკეტი მშრალი ყვავილებით"],
   en:["Little Surprise","A mini bouquet of dried flowers"]},
];

const ZONES = [
  ["ვაკე","Vake",10],["საბურთალო","Saburtalo",10],["მთაწმინდა","Mtatsminda",12],
  ["ძველი თბილისი","Old Tbilisi",12],["ვერე","Vere",12],["დიდუბე","Didube",15],
  ["ჩუღურეთი","Chugureti",15],["ნაძალადევი","Nadzaladevi",18],["ისანი","Isani",18],
  ["დიღომი","Dighomi",20],["გლდანი","Gldani",20],["სამგორი","Samgori",20],["ვარკეთილი","Varketili",20],
];
const FREE_FROM = 300;

const COLORS = [
  ["pink","#f1a7b5","ვარდისფერი","Pink"],["red","#c0283e","წითელი","Red"],
  ["white","#f7f3ec","თეთრი","White"],["peach","#f6c29b","ატმისფერი","Peach"],
  ["yellow","#f5d44c","ყვითელი","Yellow"],["purple","#9b7fd1","იისფერი","Purple"],
];

const T = {
  en:{
    nav_shop:"Bouquets",nav_custom:"Make your own",nav_events:"Events",nav_delivery:"Delivery",nav_contact:"Contact",
    hero_eyebrow:"Flower studio · Tbilisi",hero_title:"Flowers that say more than words",
    hero_lead:"Every bouquet is hand-tied with flowers that arrived that same morning. Order in a minute, delivered the same day.",
    hero_cta:"Choose a bouquet",hero_cta2:"Make your own",
    b1_t:"2 hrs",b1_s:"delivery in Tbilisi",b2_t:"Daily",b2_s:"fresh flowers",b3_t:"Photo",b3_s:"before delivery",
    hero_card:"A free card with your own words on every order",
    shop_eyebrow:"Catalogue",shop_title:"Today's bouquets",
    f_all:"All",f_love:"Love",f_birthday:"Birthday",f_wedding:"Wedding",f_vase:"In a vase",
    how_title:"How it works",
    s1_t:"Pick a bouquet",s1_p:"Or describe what you want and we'll make it.",
    s2_t:"Order on WhatsApp",s2_p:"Your order is filled in for you, just hit send.",
    s3_t:"Get a photo",s3_p:"We send you a photo of the finished bouquet before it leaves.",
    s4_t:"We deliver",s4_p:"Within 2 hours in Tbilisi, or at the time you choose.",
    c_eyebrow:"Custom order",c_title:"Create your own bouquet",
    c_lead:"Pick a budget and colours, and our florist will message you to make it together.",
    c_budget:"Budget",c_colors:"Colours",c_note:"What's it for? (optional)",c_note_ph:"e.g. Mum's birthday",c_send:"Send on WhatsApp",
    e_eyebrow:"Weddings & events",e_title:"Big flowers for big days",
    e_p:"Bridal bouquets, table centrepieces, arches and venue styling. Send us your date and idea and we'll offer a free consultation.",
    e_l1:"Bridal bouquets and boutonnières",e_l2:"Table and venue styling",e_l3:"Weekly corporate flowers",e_cta:"Request a consultation",
    d_eyebrow:"Delivery",d_title:"We deliver all over Tbilisi",
    d_note:"Order before 18:00 for same-day delivery. Free delivery on orders over 300 ₾.",
    ct_title:"Visit us",ct_addr_l:"Address",ct_addr:"Vake, Tbilisi",ct_hours_l:"Opening hours",ct_hours:"Every day 09:00–21:00",ct_wa:"Message us",
    foot:"Demo website. Made by Luka.",
    o_date:"Delivery date",o_zone:"District",o_card:"Card message (optional)",o_card_ph:"e.g. Happy birthday, Mum! ❤",
    o_total:"Total",o_send:"Order on WhatsApp",order:"Order",free:"free",m_delivery:"delivery",
    tag_hit:"Bestseller",tag_vase:"With vase",tag_premium:"Premium",
    m_hi:"Hello Rose! I'd like to order:",m_bouquet:"Bouquet",m_date:"Delivery",m_zone:"District",m_card:"Card",m_total:"Total",
    m_custom:"Hello Rose! I'd like a custom bouquet.",m_budget:"Budget",m_colors:"Colours",m_for:"For",
    m_event:"Hello Rose! I'd like a consultation for an event.",m_hello:"Hello Rose!",
  },
  ka:{
    order:"შეკვეთა",free:"უფასო",m_delivery:"მიტანა",tag_hit:"ფავორიტი",tag_vase:"ვაზით",tag_premium:"პრემიუმი",
    m_hi:"გამარჯობა, Rose! მინდა შევუკვეთო:",m_bouquet:"ბუკეტი",m_date:"მიტანა",m_zone:"უბანი",m_card:"ბარათი",m_total:"ჯამი",
    m_custom:"გამარჯობა, Rose! მინდა ინდივიდუალური ბუკეტი.",m_budget:"ბიუჯეტი",m_colors:"ფერები",m_for:"რისთვის",
    m_event:"გამარჯობა, Rose! მინდა კონსულტაცია ღონისძიებისთვის.",m_hello:"გამარჯობა, Rose!",
  },
};

const $ = s => document.querySelector(s);
let lang = "ka";
try { lang = localStorage.getItem("rose-lang") || "ka"; } catch {}
// Georgian UI strings live in the HTML; capture them once so switching back works.
document.querySelectorAll("[data-i18n]").forEach(el => T.ka[el.dataset.i18n] ??= el.textContent);
document.querySelectorAll("[data-i18n-ph]").forEach(el => T.ka[el.dataset.i18nPh] ??= el.placeholder);
const t = k => T[lang][k] ?? T.ka[k];
const L = i => lang === "ka" ? 0 : 1; // index into [ka, en] pairs
const wa = text => `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(text)}`;
const gel = n => `${n} ₾`;

function renderGrid(cat = $(".chip.on").dataset.cat) {
  $("#grid").innerHTML = BOUQUETS.filter(b => cat === "all" || b.cat.includes(cat)).map(b => {
    const [name, desc] = b[lang];
    return `<article class="item">
      <div class="ph"><img src="img/${b.img}.jpg" alt="${name}" loading="lazy" width="800" height="1000">
      ${b.tag ? `<span class="tag">${t("tag_" + b.tag)}</span>` : ""}</div>
      <h3>${name}</h3><p>${desc}</p>
      <div class="row"><span class="pr">${gel(b.price)}</span>
      <button class="btn" type="button" data-order="${b.id}">${t("order")}</button></div>
    </article>`;
  }).join("");
}

function renderZones() {
  $("#zones").innerHTML = ZONES.map(z => `<div class="zone"><span>${z[L()]}</span><b>${gel(z[2])}</b></div>`).join("");
  $("#oZone").innerHTML = ZONES.map((z, i) => `<option value="${i}">${z[L()]} · ${gel(z[2])}</option>`).join("");
}

function renderSwatches() {
  const checked = new Set([...document.querySelectorAll("#swatches input:checked")].map(i => i.value));
  $("#swatches").innerHTML = COLORS.map(([id, hex, ka, en]) =>
    `<label class="sw"><input type="checkbox" value="${id}" ${checked.has(id) ? "checked" : ""}><i style="background:${hex}"></i>${lang === "ka" ? ka : en}</label>`).join("");
}

function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-ph]").forEach(el => el.placeholder = t(el.dataset.i18nPh));
  $("#lang").textContent = lang === "ka" ? "EN" : "ქარ";
  renderGrid(); renderZones(); renderSwatches();
  $("#eventBtn").href = wa(t("m_event"));
  $("#waFloat").href = $("#waText").href = wa(t("m_hello"));
}

$("#lang").onclick = () => {
  lang = lang === "ka" ? "en" : "ka";
  try { localStorage.setItem("rose-lang", lang); } catch {}
  applyLang();
};

$("#filters").onclick = e => {
  const c = e.target.closest(".chip"); if (!c) return;
  document.querySelectorAll(".chip").forEach(x => x.classList.toggle("on", x === c));
  renderGrid(c.dataset.cat);
};

// mobile menu
const burger = $("#burger"), links = $("#links");
burger.onclick = () => { const o = links.classList.toggle("open"); burger.setAttribute("aria-expanded", o); };
links.onclick = e => { if (e.target.tagName === "A") { links.classList.remove("open"); burger.setAttribute("aria-expanded", false); } };
addEventListener("scroll", () => $(".nav").classList.toggle("scrolled", scrollY > 10), {passive:true});

// order dialog
const dlg = $("#orderDlg");
let current = null;
function total() {
  const fee = current.price >= FREE_FROM ? 0 : ZONES[$("#oZone").value][2];
  return {fee, sum: current.price + fee};
}
function updateTotal() {
  const {fee, sum} = total();
  $("#oTotal").textContent = gel(sum);
  $("#oFee").textContent = `(${t("m_bouquet").toLowerCase()} ${gel(current.price)} + ${t("m_delivery")} ${fee ? gel(fee) : t("free")})`;
}
$("#grid").onclick = e => {
  const b = e.target.closest("[data-order]"); if (!b) return;
  current = BOUQUETS.find(x => x.id === b.dataset.order);
  $("#dlgImg").src = `img/${current.img}.jpg`;
  $("#dlgTitle").textContent = current[lang][0];
  $("#dlgPrice").textContent = gel(current.price);
  const d = $("#oDate"), today = new Date().toLocaleDateString("en-CA");
  d.min = today; if (!d.value || d.value < today) d.value = today;
  updateTotal();
  dlg.showModal();
};
$("#oZone").onchange = updateTotal;
dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close(); }); // click on backdrop
$("#orderForm").addEventListener("submit", e => {
  if (e.submitter?.value !== "send") return;
  const z = ZONES[$("#oZone").value], card = $("#oCard").value.trim();
  const msg = [t("m_hi"),
    `${t("m_bouquet")}: ${current[lang][0]} (${gel(current.price)})`,
    `${t("m_date")}: ${$("#oDate").value}`,
    `${t("m_zone")}: ${z[L()]}`,
    card && `${t("m_card")}: "${card}"`,
    `${t("m_total")}: ${gel(total().sum)}`].filter(Boolean).join("\n");
  window.open(wa(msg), "_blank", "noopener");
});

// custom bouquet
const budget = $("#budget");
budget.oninput = () => $("#budgetOut").textContent = gel(budget.value);
$("#customForm").onsubmit = e => {
  e.preventDefault();
  const cols = [...document.querySelectorAll("#swatches input:checked")]
    .map(i => COLORS.find(c => c[0] === i.value)[lang === "ka" ? 2 : 3]);
  const note = $("#cNote").value.trim();
  const msg = [t("m_custom"), `${t("m_budget")}: ${gel(budget.value)}`,
    cols.length && `${t("m_colors")}: ${cols.join(", ")}`, note && `${t("m_for")}: ${note}`].filter(Boolean).join("\n");
  window.open(wa(msg), "_blank", "noopener");
};

applyLang();
