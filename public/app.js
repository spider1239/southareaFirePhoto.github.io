const galleryRoot = document.querySelector("#gallery-root");
const galleryTitle = document.querySelector("#gallery-title");
const gallerySummary = document.querySelector("#gallery-summary");
const categoryNav = document.querySelector("#category-nav");
const categoryTemplate = document.querySelector("#category-template");
const cardTemplate = document.querySelector("#card-template");
const lightbox = document.querySelector("#lightbox");
const lightboxImage = document.querySelector("#lightbox-image");
const lightboxTitle = document.querySelector("#lightbox-title");
const lightboxCategory = document.querySelector("#lightbox-category");
const lightboxDownload = document.querySelector("#lightbox-download");
const lightboxShare = document.querySelector("#lightbox-share");

let currentLightboxItem = null;
const navGroupOrder = ["新人組", "公開組", "團舞", "其他"];

function slugifyCategoryName(name) {
  return `category-${name.normalize("NFKD").replace(/[^\w\u4e00-\u9fff-]+/g, "-")}`;
}

async function loadGallery() {
  const response = await fetch(`./gallery-data.json?ts=${Date.now()}`);
  if (!response.ok) {
    throw new Error("無法讀取相簿資料");
  }
  return response.json();
}

function absoluteUrl(relativePath) {
  return new URL(relativePath, window.location.href).toString();
}

async function sharePhoto(item) {
  const shareUrl = item.shareUrl
    ? absoluteUrl(item.shareUrl)
    : absoluteUrl(item.src);
  const shareData = {
    title: item.name,
    text: `${item.category} - ${item.name}`,
    url: shareUrl,
  };

  if (navigator.share) {
    try {
      await navigator.share(shareData);
      return;
    } catch (error) {
      if (error?.name === "AbortError") {
        return;
      }
    }
  }

  await navigator.clipboard.writeText(shareUrl);
  window.alert("已複製照片連結");
}

function openLightbox(item) {
  currentLightboxItem = item;
  lightboxImage.src = item.src;
  lightboxImage.alt = item.name;
  lightboxTitle.textContent = item.name;
  lightboxCategory.textContent = item.category;
  lightboxDownload.href = item.download;
  lightboxDownload.download = item.filename;
  lightboxShare.dataset.src = item.src;
  lightbox.showModal();
}

function createPhotoCard(categoryName, item) {
  const fragment = cardTemplate.content.cloneNode(true);
  const button = fragment.querySelector(".photo-button");
  const image = fragment.querySelector(".photo-image");
  const name = fragment.querySelector(".photo-name");
  const download = fragment.querySelector('[data-role="download"]');
  const share = fragment.querySelector('[data-role="share"]');
  const photoItem = { ...item, category: categoryName };

  image.src = item.previewSrc || item.src;
  image.alt = item.name;
  image.loading = "lazy";
  image.decoding = "async";
  image.fetchPriority = "low";
  name.textContent = item.name;
  download.href = item.download;
  download.download = item.filename;

  button.addEventListener("click", () => openLightbox(photoItem));
  share.addEventListener("click", () => sharePhoto(photoItem));

  return fragment;
}

function renderCategoryNav(categories) {
  const fragment = document.createDocumentFragment();
  const groupedCategories = {};

  for (const category of categories) {
    const groupName = category.group || "其他";
    if (!groupedCategories[groupName]) {
      groupedCategories[groupName] = [];
    }
    groupedCategories[groupName].push(category);
  }

  for (const groupName of navGroupOrder) {
    const items = groupedCategories[groupName];
    if (!items?.length) {
      continue;
    }

    const details = document.createElement("details");
    details.className = "nav-group";
    details.open = true;

    const summary = document.createElement("summary");
    summary.className = "nav-group-summary";
    summary.textContent = `${groupName} (${items.length})`;
    details.append(summary);

    const links = document.createElement("div");
    links.className = "nav-group-links";

    for (const category of items) {
      const link = document.createElement("a");
      link.className = "category-nav-link";
      link.href = `#${slugifyCategoryName(category.name)}`;
      link.textContent = category.name;
      links.append(link);
    }

    details.append(links);
    fragment.append(details);
  }

  categoryNav.replaceChildren(fragment);
}

function renderGallery(data) {
  galleryTitle.textContent = `${data.title} 相簿`;
  gallerySummary.textContent = `共 ${data.categoryCount} 個分類，${data.imageCount} 張照片。可直接預覽、下載或分享單張照片。`;
  renderCategoryNav(data.categories);

  const content = document.createDocumentFragment();

  for (const category of data.categories) {
    const fragment = categoryTemplate.content.cloneNode(true);
    const section = fragment.querySelector(".category-section");
    section.id = slugifyCategoryName(category.name);
    const title = fragment.querySelector(".category-title");
    title.textContent = category.name;
    fragment.querySelector(".category-count").textContent = `${category.count} 張照片`;
    const grid = fragment.querySelector(".photo-grid");
    const emptyState = fragment.querySelector(".category-empty");

    for (const item of category.images) {
      grid.append(createPhotoCard(category.name, item));
    }

    emptyState.hidden = category.images.length > 0;

    content.append(fragment);
  }

  galleryRoot.replaceChildren(content);
}

lightboxShare.addEventListener("click", () => {
  if (currentLightboxItem) {
    sharePhoto(currentLightboxItem);
  }
});

loadGallery()
  .then(renderGallery)
  .catch((error) => {
    console.error(error);
    gallerySummary.textContent = "載入相簿失敗，請重新執行建置腳本。";
  });
