import { useState, useRef } from "react";
import { Upload, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { uploadDocumentForAutofill, DocumentUploadResponse } from "@/lib/recommend";

export function AutofillUpload({ onUploadComplete }: { onUploadComplete: (data: DocumentUploadResponse) => void }) {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (file.type !== "application/pdf") {
      toast.error("Please upload a PDF document.");
      return;
    }
    
    setIsUploading(true);
    try {
      const response = await uploadDocumentForAutofill(file);
      toast.success("Document analyzed successfully!");
      onUploadComplete(response);
    } catch (err) {
      toast.error("Failed to process document. Please try again or fill manually.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="rounded-2xl border border-dashed border-border bg-card p-10 text-center shadow-sm">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="application/pdf"
      />
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
        {isUploading ? (
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        ) : (
          <Upload className="h-8 w-8 text-primary" />
        )}
      </div>
      <h3 className="mb-2 text-xl font-semibold">
        {isUploading ? "Analyzing Document..." : "Upload Sustainability Report"}
      </h3>
      <p className="mb-6 text-sm text-muted-foreground mx-auto max-w-md">
        Upload your latest ESG, annual, or sustainability report (PDF) and we'll automatically extract your profile details.
      </p>
      <Button 
        onClick={() => fileInputRef.current?.click()} 
        disabled={isUploading}
        size="lg"
        className="rounded-full px-8"
      >
        {isUploading ? "Extracting insights..." : "Select PDF File"}
      </Button>
    </div>
  );
}
