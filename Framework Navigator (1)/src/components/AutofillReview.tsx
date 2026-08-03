import { useState } from "react";
import { Check, X, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DocumentUploadResponse, OrgProfile, emptyProfile } from "@/lib/recommend";
import { Checkbox } from "@/components/ui/checkbox";

export function AutofillReview({ 
  data, 
  onApply 
}: { 
  data: DocumentUploadResponse; 
  onApply: (profile: OrgProfile) => void 
}) {
  // Track which suggestions the user has accepted (default to all > 0.6 confidence)
  const [acceptedFields, setAcceptedFields] = useState<Set<string>>(
    new Set(data.suggestions.filter(s => s.confidence >= 0.6).map(s => s.field))
  );

  const toggleField = (field: string) => {
    const newSet = new Set(acceptedFields);
    if (newSet.has(field)) {
      newSet.delete(field);
    } else {
      newSet.add(field);
    }
    setAcceptedFields(newSet);
  };

  const handleApply = () => {
    const merged: OrgProfile = { ...emptyProfile };
    
    // Group suggestions by field to handle arrays (e.g. existing_certifications, goals)
    const lists: Record<string, string[]> = { certifications: [], goals: [] };

    data.suggestions.forEach(s => {
      if (!acceptedFields.has(s.field)) return;

      if (s.field === "existing_certifications") {
        if (Array.isArray(s.suggested_value)) {
          lists.certifications.push(...s.suggested_value);
        } else {
          lists.certifications.push(s.suggested_value);
        }
      } else if (s.field === "sustainability_goals") {
        if (Array.isArray(s.suggested_value)) {
          lists.goals.push(...s.suggested_value);
        } else {
          lists.goals.push(s.suggested_value);
        }
      } else {
        // Simple mapping
        const keyMap: Record<string, keyof OrgProfile> = {
          industry: "industry",
          org_size: "size",
          region: "region",
          annual_energy_use_level: "energyUse",
          emissions_tracking_maturity: "emissionsMaturity",
          disclosure_level: "disclosure"
        };
        const mappedKey = keyMap[s.field];
        if (mappedKey) {
          (merged as any)[mappedKey] = s.suggested_value;
        }
      }
    });

    merged.certifications = [...new Set(lists.certifications)];
    merged.goals = [...new Set(lists.goals)];

    onApply(merged);
  };

  const formatFieldName = (field: string) => {
    return field.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-border bg-card p-6 shadow-card sm:p-8">
        <div className="mb-6 flex items-center justify-between border-b pb-4">
          <div>
            <h2 className="text-xl font-semibold">Autofill Suggestions</h2>
            <p className="text-sm text-muted-foreground mt-1">
              We extracted these insights from your document. Review and uncheck any incorrect values.
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-primary">{Math.round(data.overall_confidence * 100)}%</div>
            <div className="text-xs text-muted-foreground uppercase tracking-wider">Confidence</div>
          </div>
        </div>

        {data.suggestions.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">
            No actionable signals found in this document.
          </div>
        ) : (
          <div className="space-y-4">
            {data.suggestions.map((suggestion, idx) => (
              <div 
                key={idx} 
                className={`flex gap-4 rounded-xl border p-4 transition-colors ${
                  acceptedFields.has(suggestion.field) ? 'border-primary/40 bg-secondary/30' : 'border-border bg-background opacity-60'
                }`}
              >
                <div className="pt-1">
                  <Checkbox 
                    checked={acceptedFields.has(suggestion.field)} 
                    onCheckedChange={() => toggleField(suggestion.field)} 
                  />
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        {formatFieldName(suggestion.field)}
                      </div>
                      <div className="mt-1 font-medium text-navy">
                        {Array.isArray(suggestion.suggested_value) 
                          ? suggestion.suggested_value.join(", ") 
                          : String(suggestion.suggested_value)}
                      </div>
                    </div>
                    <div className="text-xs font-medium px-2 py-1 rounded-md bg-secondary text-primary">
                      {Math.round(suggestion.confidence * 100)}% Match
                    </div>
                  </div>
                  {suggestion.source_snippet && (
                    <div className="mt-3 flex gap-2 rounded-md bg-muted/50 p-3 text-xs text-muted-foreground">
                      <Info className="mt-0.5 h-4 w-4 shrink-0" />
                      <div>
                        <span className="italic">"{suggestion.source_snippet}"</span>
                        <div className="mt-1 font-medium text-foreground/70">{suggestion.reason}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 flex justify-end gap-3 pt-4 border-t">
          <Button variant="outline" onClick={() => onApply(emptyProfile)}>
            Discard & Fill Manually
          </Button>
          <Button onClick={handleApply}>
            Apply Selected to Profile
          </Button>
        </div>
      </div>
    </div>
  );
}
