"use client";

type WelcomeScreenProps = {
  onUploadFiles: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onCreateNew: () => void;
};

export default function WelcomeScreen({
  onUploadFiles,
  onCreateNew,
}: WelcomeScreenProps) {
  return (
    <div className="flex items-center gap-64">
      {/* Upload File Icon */}
      <div className="flex flex-col items-center cursor-pointer transition-transform hover:scale-110 active:scale-95">
        <img
          src="/icons/upload-icon.svg"
          alt="Upload Files"
          className="w-16 h-16 filter invert"
          onClick={() => document.getElementById("file-input")?.click()}
        />
        <label className="text-white mt-2">Upload Files</label>
        <input
          id="file-input"
          type="file"
          accept=".py,.kt,.java,.cs"
          onChange={onUploadFiles}
          className="hidden"
        />
      </div>

      {/* Divider */}
      <div className="h-125 border-l-2 border-white" />

      {/* Write Code Icon */}
      <div
        className="flex flex-col items-center cursor-pointer transition-transform hover:scale-110 active:scale-95"
        onClick={onCreateNew}
      >
        <img
          src="/icons/write-icon.svg"
          alt="Write Code"
          className="w-16 h-16 filter invert"
        />
        <label className="text-white mt-2">Write Code</label>
      </div>
    </div>
  );
}
