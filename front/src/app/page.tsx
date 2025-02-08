"use client"

import { DataTable } from "@/components/datatable";
import { ArticleCard } from "@/components/articlecard";
import { DummyForm } from "@/components/dummyform";
import { listArticles, Article, createDummy, deleteDummy, extractArticles, GeneratedArticle } from "@/lib/api/articleGateway"; // updated import
import { on } from "events";
import { useEffect, useState } from "react";
import { set } from "react-hook-form";
import { Input } from "@/components/ui/input";

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
    (async () => {
      const dummyData = await listArticles();
      setData(dummyData);
      console.log(getColumnsFromData(dummyData));
      setColumns(getColumnsFromData(dummyData));
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
    // const stockMatch = stockQuery === "" || d.stocks.some(s => s.toLowerCase().includes(stockQuery.toLowerCase()));
    // const urlMatch = urlQuery === "" || (d.sourceUrl?.toLowerCase().includes(urlQuery.toLowerCase()));
    // return stockMatch && urlMatch;
  });

  return (
    <div className="container mx-auto my-10 max-w-3xl">
      <div className="my-10">
        <h1 className="text-4xl font-bold">Sick finance</h1>
        <div className="grid grid-cols-2 gap-2 my-4">
          {/* updated inputs with onChange handlers */}
          <Input
            placeholder="stock"
            type="text"
            value={stockQuery}
            onChange={(e) => setStockQuery(e.target.value)}
          />
          <Input
            placeholder="Source URL"
            type="url"
            value={urlQuery}
            onChange={(e) => setUrlQuery(e.target.value)}
          />
        </div>
        {/* new form to trigger PUT request */}
        <form onSubmit={onExtractSubmit} className="my-4">
          <Input
            placeholder="Enter URL to extract articles"
            type="url"
            value={extractUrl}
            onChange={(e) => setExtractUrl(e.target.value)}
          />
          <button type="submit" className="px-2 py-1 ml-2 bg-blue-500 text-white rounded">
            Extract Articles
          </button>
        </form>
      </div>

      <div className="max-w-3xl mx-auto grid grid-cols-1 gap-4">
        {filteredData.map((d) => (
          <ArticleCard key={d.id} request={d} onClick={onClick} />
        ))}
      </div>
    </div>

  );
}
