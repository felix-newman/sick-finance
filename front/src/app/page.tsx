"use client"

import { DataTable } from "@/components/datatable";
import { ArticleCard } from "@/components/articlecard";
import { DummyForm } from "@/components/dummyform";
import { listArticles, Article, createDummy, deleteDummy } from "@/lib/api/articleGateway";
import { on } from "events";
import { useEffect, useState } from "react";
import { set } from "react-hook-form";
import { Input } from "@/components/ui/input";

export default function DemoPage() {
  const [data, setData] = useState<Article[]>([]);
  const [columns, setColumns] = useState<{ header: string, accessorKey: string }[]>([]);

  function getColumnsFromData(data: Article[]): { header: string; accessorKey: string }[] {
    if (!data.length) return [];
    return Object.keys(data[0]).map((key) => ({
      header: key.charAt(0).toUpperCase() + key.slice(1),
      accessorKey: key, // Use accessorKey here
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
  const onClick = (data: Article) => {
    window.location.href = `/${data.title}`;
  }

  const onDeleteClicked = async (data: Article) => {
    await deleteDummy(data.id as string)
    setData(await listArticles())
    console.log(data)
  }

  return (
    <div className="container mx-auto my-10 max-w-3xl">
      <div className="my-10">
        <h1 className="text-4xl font-bold">Sick finance</h1>
        <div className="grid grid-cols-2 gap-2 my-4">
          <Input
            placeholder="stock"
            type="text"
          />
          <Input
            placeholder="Source URL"
            type="url"
          />
        </div>
      </div>

      <div className="max-w-3xl mx-auto grid grid-cols-1 gap-4">
        {data.map((d) => (
          <ArticleCard key={d.id} request={d} onClick={onClick} />
        ))}
      </div>
    </div>

  );
}
