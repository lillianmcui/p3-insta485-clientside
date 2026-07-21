import Post from "./post";
import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";

export default function Feed() {
  const [posts, setPosts] = useState(null);
  const [nextUrl, setNext] = useState("/api/v1/posts/");
  const [hasMore, setMore] = useState(true);

  function fetchPosts(fetchUrl) {
    if (!fetchUrl) return;

    fetch(fetchUrl, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPosts((currPosts) => [...(currPosts || []), ...data.results]);
        setNext(data.next || null);
        setMore(Boolean(data.next));
      })
      .catch((error) => console.log(error));
  }

  useEffect(() => {
    let ignoreStaleRequest = false;

    fetch("/api/v1/posts/", { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (ignoreStaleRequest) return;
        setPosts(data.results);
        setNext(data.next || null);
        setMore(Boolean(data.next));
      })
      .catch((error) => console.error("feed load failed:", error));

    return () => {
      ignoreStaleRequest = true;
    };
  }, []);

  if (posts == null) {
    return <div className="post">Loading...</div>;
  }
  return (
    <InfiniteScroll
      dataLength={posts.length}
      next={() => fetchPosts(nextUrl)}
      hasMore={hasMore}
      loader={<div className="post">Loading...</div>}
    >
      {posts.map((post) => (
        <Post key={post.postid} url={post.url}></Post>
      ))}
    </InfiniteScroll>
  );
}
