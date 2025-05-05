type PlaylistItem = {
  id: string;
  snippet: {
    title: string;
  };
};

type PlaylistProps = {
  playlist: PlaylistItem[];  // Expecting playlist prop to be an array of PlaylistItem
};

const Playlist = ({ playlist }: PlaylistProps) => {
  return (
    <div>
      <h2 className="text-2xl mt-5" style={{ fontFamily: "var(--font-permanent-marker)" }}>
        Playlist:
      </h2>
      <ul className="list-disc list-inside text-justify my-4 mx-2 px-2">
        {playlist.map((item) => (
          <li key={item.id}>{item.snippet.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default Playlist;
