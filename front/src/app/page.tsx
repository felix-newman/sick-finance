"use client"

import { DataTable } from "@/components/datatable";
import { ArticleCard } from "@/components/articlecard";
import { DummyForm } from "@/components/dummyform";
import { listArticles, Article, createDummy, deleteDummy, extractArticles, GeneratedArticle } from "@/lib/api/articleGateway"; // updated import
import { on } from "events";
import { useEffect, useState } from "react";
import { set } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function DemoPage() {
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
    let cancelled = false;
    async function fetchData() {
      const dummyData = await listArticles();
      if (cancelled) return;
      setData(dummyData);
      setTimeout(fetchData, 10_000); // schedule next fetch 5s after finish
    }
    fetchData();
    return () => { cancelled = true; }
  }, []);

  const onSubmit = async (values: any) => {
    await createDummy(values.name)
    // # update dummies
    setData(await listArticles())
  }
  const onClick = (data: GeneratedArticle) => {
    window.location.href = encodeURIComponent(`${data.title}`);
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
    <div className="container mx-auto my-10 max-w-3xl">
      <div className="my-10">
        <h1 className="text-4xl font-bold">Sick finance</h1>
        
        <form onSubmit={onExtractSubmit} className="my-4">
          <Input
            placeholder="Enter URL to extract articles"
            type="url"
            value={extractUrl}
            onChange={(e) => setExtractUrl(e.target.value)}
          />
          <div className="flex justify-end">
          <Button type="submit" className="my-2">
            Extract Articles
          </Button>
          </div>
        </form>  
        
        
        <div className="grid grid-cols-2 gap-2 my-4">
          {/* updated inputs with onChange handlers */}
          <Input
            placeholder="stock"
            type="text"
            value={stockQuery}
            onChange={(e) => setStockQuery(e.target.value)}
          />
          <div></div>
        </div>
  
       
      </div>

      <div className="max-w-3xl mx-auto grid grid-cols-1 gap-4">
        {filteredData.map((d) => (
          <ArticleCard key={d.id} request={d} onClick={onClick} />
        ))}
      </div>
    </div>

  );
}
