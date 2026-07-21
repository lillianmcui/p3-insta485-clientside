import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import Comment from "./comment";

dayjs.extend(relativeTime);
dayjs.extend(utc);

export default function Post({ url }) {
  const [imgUrl, setImgUrl] = useState(null);
  const [owner, setOwner] = useState(null);
  const [ownerImgUrl, setOwnerImgUrl] = useState(null);
  const [now, setNow] = useState(dayjs());
  const [likes, setLikes] = useState(null);
  const [created, setCreated] = useState(null);
  const [showUrl, setShowUrl] = useState(null);
  const [postid, setPostid] = useState(null);
  const [comments, setComments] = useState([]);
  const [newCommentText, setNewCommentText] = useState("");

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(dayjs());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    let ignoreStaleRequest = false;

    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setOwnerImgUrl(data.ownerImgUrl);
          setLikes(data.likes);
          setCreated(data.created);
          setShowUrl(data.postShowUrl);
          setPostid(data.postid);
          setComments(data.comments || []);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      ignoreStaleRequest = true;
    };
  }, [url]);

  async function handleClick() {
    if (likes.lognameLikesThis) {
      if (!likes.url) return;

      try {
        console.log("DELETE ->", likes.url);
        const response = await fetch(likes.url, {
          method: "DELETE",
          credentials: "same-origin",
        });
        if (!response.ok) throw Error(response.statusText);

        setLikes((prevLikes) => ({
          ...prevLikes,
          numLikes: prevLikes.numLikes - 1,
          lognameLikesThis: false,
          url: null,
        }));
      } catch (error) {
        console.log(error);
      }
    } else {
      try {
        const response = await fetch(`/api/v1/likes/?postid=${postid}`, {
          method: "POST",
          credentials: "same-origin",
        });
        if (!response.ok) throw Error(response.statusText);
        const data = await response.json();
        console.log("like POST returned:", data);
        setLikes((prevLikes) => ({
          ...prevLikes,
          numLikes: prevLikes.numLikes + 1,
          lognameLikesThis: true,
          url: data.url,
        }));
      } catch (error) {
        console.log(error);
      }
    }
  }

  function handleDoubleClick() {
    if (!likes.lognameLikesThis) {
      handleClick();
    }
  }

  async function handleSubmitComment() {
    if (!newCommentText.trim()) return;

    try {
      const response = await fetch(`/api/v1/comments/?postid=${postid}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: newCommentText }),
        credentials: "same-origin",
      });
      if (!response.ok) throw Error(response.statusText);
      const createdComment = await response.json();
      console.log(createdComment);
      setNewCommentText("");
      setComments((prevComments) => [...prevComments, createdComment]);
    } catch (error) {
      console.log(error);
    }
  }

  async function handleDeleteComment(commentid) {
    try {
      const response = await fetch(`/api/v1/comments/${commentid}/`, {
        method: "DELETE",
        credentials: "same-origin",
      });
      if (!response.ok) throw Error(response.statusText);
      setComments((prevComments) =>
        prevComments.filter((comment) => comment.commentid !== commentid)
      );
    } catch (error) {
      console.log(error);
    }
  }

  if (imgUrl === null || owner === null || likes === null || created === null) {
    return (
      <div className="post">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="post">
      <img src={imgUrl} alt="post_image" onDoubleClick={handleDoubleClick} />
      <p>{owner}</p>
      <img className="pfp" src={ownerImgUrl} alt="owner_image"/>
      <a href={showUrl} data-testid="post-time-ago">
        {dayjs.utc(created).fromNow()}
      </a>
      <button data-testid="like-unlike-button" type="button" onClick={handleClick}>
        {likes.lognameLikesThis ? "Unlike" : "Like"}
      </button>
      <p>
        {likes.numLikes} {likes.numLikes === 1 ? "like" : "likes"}
      </p>
      {comments.map((comment) => (
        <Comment key={comment.commentid} comment={comment} onDelete={handleDeleteComment} />
      ))}
      <form data-testid="comment-form" onSubmit={e => {
      e.preventDefault();
      handleSubmitComment();
      }}>
        <input
          type="text"
          value={newCommentText}
          onChange={(e) => setNewCommentText(e.target.value)}
        />
      </form>
    </div>
  );
}