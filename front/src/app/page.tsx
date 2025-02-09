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
import { Source } from "@/types/source"
import { SourceDropdown } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge"

export default function Home() {
  const [data, setData] = useState<GeneratedArticle[]>([]);
  const [columns, setColumns] = useState<{ header: string, accessorKey: string }[]>([]);
  
  // added search state
  const [stockQuery, setStockQuery] = useState("");
  const [urlQuery, setUrlQuery] = useState("");

  // new extractArticles form state
  const [extractUrl, setExtractUrl] = useState("https://globenewswire.com/NewsRoom?page=1&pageSize=10");

  const [sources, setSources] = useState<Source[]>([])
  const [selectedSources, setSelectedSources] = useState<Source[]>([])

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

  useEffect(() => {
    const fetchSources = async () => {
      try {
        const response = await fetch('http://localhost:8000/sources')
        if (!response.ok) {
          throw new Error('Failed to fetch sources')
        }
        const data = await response.json()
        setSources(data)
      } catch (error) {
        console.error('Error fetching sources:', error)
      }
    }

    fetchSources()
  }, []) // Empty dependency array means this runs once on mount

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
    const sourceMatch = urlQuery === "" || d.source_url?.toLowerCase().includes(urlQuery.toLowerCase());
    return stockMatch && sourceMatch;
  });

  const handleSourceSelect = (source: Source) => {
    console.log('Selected source:', source)
    if (!selectedSources.some(s => s.id === source.id)) {
      setSelectedSources(prev => [...prev, source])
    }
    setExtractUrl(source.url)
  }

  const handleRemoveSource = (sourceId: string) => {
    setSelectedSources(prev => prev.filter(s => s.id !== sourceId))
  }

  const handleAddSource = async (url: string) => {
    try {
      const newSource = { url, id: crypto.randomUUID() }
      const response = await fetch('http://localhost:8000/sources', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSource),
      })

      if (!response.ok) {
        throw new Error('Failed to add source')
      }

      // Refresh sources list
      const updatedSources = await fetch('http://localhost:8000/sources').then(res => res.json())
      setSources(updatedSources)
      
      // Add to selected sources
      setSelectedSources(prev => [...prev, newSource])
      setExtractUrl(url)

      // Extract articles from the new source
      const extractedArticles = await extractArticles(url)
      console.log('Extracted articles:', extractedArticles)
      
      // Refresh articles list
      const updatedArticles = await listArticles()
      setData(updatedArticles)
    } catch (error) {
      console.error('Error adding source:', error)
    }
  }

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

      <div className="space-y-4">
        <SourceDropdown 
          sources={sources} 
          onSourceSelect={handleSourceSelect}
          onAddSource={handleAddSource}
        />
        
        {selectedSources.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedSources.map(source => (
              <Badge 
                key={source.id}
                variant="secondary"
                onRemove={() => handleRemoveSource(source.id)}
              >
                {source.url}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-6">
        {filteredData.map((article) => (
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
