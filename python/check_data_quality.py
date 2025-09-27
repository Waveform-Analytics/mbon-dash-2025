#!/usr/bin/env python3

import pandas as pd

# Load the aligned dataset
df = pd.read_parquet('../data/processed/aligned_dataset_2021.parquet')

print('Dataset shape:', df.shape)
print()

print('Missing data by column type:')
print('Detection columns:')
det_cols = ['Silver perch', 'Black drum', 'Vessel']
for col in det_cols:
    if col in df.columns:
        print(f'  {col}: {df[col].isna().mean()*100:.1f}% missing')

print()
print('Environmental columns:')
env_cols = ['Water temp (°C)', 'Water depth (m)']
for col in env_cols:
    if col in df.columns:
        print(f'  {col}: {df[col].isna().mean()*100:.1f}% missing')

print()
print('SPL columns:')
spl_cols = [col for col in df.columns if 'spl_' in col]
for col in spl_cols[:3]:
    if col in df.columns:
        print(f'  {col}: {df[col].isna().mean()*100:.1f}% missing')

print()
print('Acoustic indices (sample):')
acoustic_cols = ['ZCR', 'MEANt', 'ACI', 'NBPEAKS']
for col in acoustic_cols:
    if col in df.columns:
        print(f'  {col}: {df[col].isna().mean()*100:.1f}% missing')

print()
print('Vessel activity summary:')
if 'Vessel' in df.columns:
    print('Total vessel detections:', df['Vessel'].sum())
    print('Percent with vessels:', (df['Vessel'] > 0).mean() * 100)
    print('Unique vessel values:', sorted(df['Vessel'].value_counts().index.tolist()))

print()
print('Date range:')
if 'datetime' in df.columns:
    print('Start:', df['datetime'].min())
    print('End:', df['datetime'].max())