export type ReviewStatus = 'planned' | 'draft' | 'in_review' | 'approved' | 'rejected';

export interface SignMetadata {
  id: string;
  label: string | null;
  description: string | null;
  regionalVariant: string | null;
  referenceSource: string | null;
  assignedAnimator: string;
  glbPath: string;
  animationClip: string;
  durationSeconds: number | null;
  reviewStatus: ReviewStatus;
  verificationEvidence: string[] | null;
  reviewerReference: string | null;
  lastUpdatedAt: string;
}
