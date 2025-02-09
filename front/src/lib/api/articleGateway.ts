const BASE_URL = "http://localhost:8000";


export interface Article {
    id: string;
    title: string;
    lead: string;
    imgUrl?: string;
    stocks: string[];
    sourceUrl?: string;
    text?: string;
  }

export interface GeneratedArticleBase {
    title: string;
    lead: string;
}

export interface GeneratedArticle extends GeneratedArticleBase {
    id: string;
    image_url: string;
    mentioned_stocks: string[];
    image_data: string;
    content: string;
    source_url: string;
}

export async function getStatus(): Promise<any> {
  const res = await fetch(`${BASE_URL}/status`);
  return res.json();
}

export async function listArticles(): Promise<GeneratedArticle[]> {
  const res = await fetch(`${BASE_URL}/generated_articles`);
  return res.json();
 
}

export async function createDummy(name: string): Promise<Article> {
  const res = await fetch(`${BASE_URL}/dummies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return res.json();
}

export async function getDummy(dummyId: string): Promise<Article> {
  const res = await fetch(`${BASE_URL}/dummies/${dummyId}`);
  return res.json();
}

export async function updateDummy(dummyId: string, data: { name: string }): Promise<void> {
  await fetch(`${BASE_URL}/dummies/${dummyId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteDummy(dummyId: string): Promise<void> {
  await fetch(`${BASE_URL}/dummies/${dummyId}`, {
    method: "DELETE",
  });
}

export async function extractArticles(url: string): Promise<Article[]> {
  const res = await fetch(`${BASE_URL}/articles/`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return res.json();
}

export async function listGeneratedArticles(): Promise<GeneratedArticle[]> {
    const res = await fetch(`${BASE_URL}/generated_articles`);
    return res.json();
}

// New endpoint call added below:
export async function getGeneratedArticleByTitle(title: string): Promise<GeneratedArticle> {
  const res = await fetch(`${BASE_URL}/generated_articles/${title}`);
  return res.json();
}

