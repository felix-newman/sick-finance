"use client"

import { DataTable } from "@/components/datatable";
import { ArticleCard } from "@/components/articlecard";
import { DummyForm } from "@/components/dummyform";
import { listArticles, Article, createDummy, deleteDummy } from "@/lib/api/articleGateway";
import { on } from "events";
import { useEffect, useState } from "react";
import { set } from "react-hook-form";

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
  const onRowClicked = (data: object) => {
    console.log(data)
  } 
  const onDeleteClicked = async (data: Article) => {
    await deleteDummy(data.id as string)
    setData(await listArticles())
    console.log(data)
  }

  return (
    <div className="container mx-auto my-10">

      

      <div className="max-w-3xl mx-auto grid grid-cols-1 gap-4">
        {data.map((d) => (
          <ArticleCard key={d.id} request={d} onClick={() => onRowClicked(d)} />
        ))}        
      </div>
    </div>

  );
}
