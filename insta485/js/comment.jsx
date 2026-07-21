import React from "react";

export default function Comment({ comment, onDelete }) {
  return (
    <div className="comment">
      <a href={comment.ownerShowUrl}>
        <span data-testid="comment-text">{comment.text}</span>
      </a>
      {comment.lognameOwnsThis && (
        <button
          type="button"
          data-testid="delete-comment-button"
          onClick={() => onDelete(comment.commentid)}
        >
          Delete
        </button>
      )}
    </div>
  );
}