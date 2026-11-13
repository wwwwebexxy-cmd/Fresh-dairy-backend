# Implementation Plan: Admin Product Variant Barcodes

## Overview
Add admin-only Code 128 barcode images for each sellable product variant and a per-product PDF download containing one label for every single-price variant and every multiple-price unit.

## Architecture Decisions
- Use the existing unique SKU as the barcode payload, generating and persisting a SKU only when an admin requests the barcode PDF. This keeps barcodes aligned with the inventory/order code and avoids a duplicate database field.
- Keep PDF rendering in the Django admin API with ReportLab, which is already a backend dependency. Protect the action through the existing `IsSuperAdmin` viewset permission.
- Show generated barcode images and values in the admin product variant view; download one printable PDF for the selected product.

## Tasks
- [x] Backend: render Code 128 SVG/PDF, ensure missing SKUs, and expose an admin-only product barcode PDF action.
- [x] Dashboard: show each sellable variant/unit barcode and add a generate/download PDF control.
- [x] Verify Django system checks and the frontend production build.

## Risks
- Existing hand-entered SKUs may contain characters unsupported by Code 128; validate them and return a clear error before returning a broken PDF.
- Multiple-price variants must produce one barcode per unit, while single-price variants produce one barcode per variant.
