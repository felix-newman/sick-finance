const BASE_URL = "http://localhost:8000";


export interface Article {
    id: string;
    title: string;
    lead: string;
    imgUrl?: string;
  }

export async function getStatus(): Promise<any> {
  const res = await fetch(`${BASE_URL}/status`);
  return res.json();
}

export async function listArticles(): Promise<Article[]> {
  // const res = await fetch(`${BASE_URL}/articles`);
  // return res.json();
  return [
    {
      id: "1",
      title: "Hello World",
      lead: "This is a dummy article",
      imgUrl: "/exmaple.png",
    },
    {
      id: "2",
      title: "Hello World 2",
      lead: "This is a dummy article",
      imgUrl: "/exmaple.png",
    }
  ]
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

