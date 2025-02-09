"use client"

import { DataTable } from "@/components/datatable";
import ArticleCard from "@/components/articlecard";
import { DummyForm } from "@/components/dummyform";
import { listArticles, Article, createDummy, deleteDummy, extractArticles, GeneratedArticle } from "@/lib/api/articleGateway"; // updated import
import { on } from "events";
import { useEffect, useState } from "react";
import { set } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function Home() {
  const [data, setData] = useState<GeneratedArticle[]>([]);
  const [columns, setColumns] = useState<{ header: string, accessorKey: string }[]>([]);
  
  // added search state
  const [stockQuery, setStockQuery] = useState("");
  const [urlQuery, setUrlQuery] = useState("");

  // new extractArticles form state
  const [extractUrl, setExtractUrl] = useState("https://globenewswire.com/NewsRoom?page=1&pageSize=10");

  function getColumnsFromData(data: Article[]): { header: string; accessorKey: string }[] {
    if (!data.length) return [];
    return Object.keys(data[0]).map((key) => ({
      header: key.charAt(0).toUpperCase() + key.slice(1),
      accessorKey: key,
    }));
  }
  useEffect(() => {
    (async () => {
      const dummyData = await listArticles();
      console.log(dummyData)
      setData(dummyData);
    })();
  }, []);

  const onSubmit = async (values: any) => {
    await createDummy(values.name)
    // # update dummies
    setData(await listArticles())
  }
  const onClick = (data: GeneratedArticle) => {
    window.location.href = `/${data.title}`;
  }

  const onDeleteClicked = async (data: Article) => {
    await deleteDummy(data.id as string)
    setData(await listArticles())
    console.log(data)
  }

  // new handler for extracting articles
  const onExtractSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const extractedArticles = await extractArticles(extractUrl);
    console.log(extractedArticles);
  };

  // filter articles using fuzzy search on stocks and sourceUrl
  const filteredData = data.filter(d => {
    const stockMatch = stockQuery === "" || d.mentioned_stocks.some(s => s.toLowerCase().includes(stockQuery.toLowerCase()));
    return stockMatch;
  });

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto">
      <h1 className="text-4xl font-bold mb-6">Sick finance</h1>
      
      <div className="mb-6">
        <input 
          type="url" 
          placeholder="https://globenewswire.com/NewsRoom?page=1&pageSize=10"
          className="w-full p-3 rounded-lg border border-gray-300"
        />
        <button className="mt-2 bg-black text-white px-6 py-2 rounded-lg float-right">
          Extract Articles
        </button>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search articles..."
          className="w-full p-3 rounded-lg border border-gray-300"
        />
      </div>

      <div className="space-y-6">
        {data.map((article) => (
          <ArticleCard
            key={article.id}
            title={article.title}
            description={article.lead}
            imageData={article.image_data}
            onClick={() => onClick(article)}
            stocks={article.mentioned_stocks}
          />
        ))}
      </div>
    </main>
  );
}
