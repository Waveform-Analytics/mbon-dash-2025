# Acoustic Indices

Understanding the acoustic indices used in biodiversity monitoring and their biological significance.

!!! info "Collaborator Data"
    The acoustic indices in this project come from collaborator analysis using established acoustic ecology methods. This page explains what each index measures and how it relates to biodiversity assessment.

## What Are Acoustic Indices?

Acoustic indices are mathematical metrics that summarize different aspects of soundscape recordings. Instead of manually identifying every species call, these indices capture patterns in the acoustic environment that may correlate with biodiversity.

**Core concept**: If we can identify which indices best predict species presence, we can automate biodiversity monitoring at scale.

## Index Categories

### Temporal Domain Indices
Measure patterns in amplitude variation over time.

| Index | Full Name | What It Measures |
|-------|-----------|------------------|
| **ZCR** | Zero Crossing Rate | Rate of signal sign changes (pitch/frequency content) |
| **MEANt** | Temporal Mean | Average amplitude over time |
| **VARt** | Temporal Variance | Amplitude variability (activity level) |
| **SKEWt** | Temporal Skewness | Asymmetry in amplitude distribution |
| **KURTt** | Temporal Kurtosis | Concentration of amplitude values |
| **LEQt** | Equivalent Sound Level (Temporal) | Energy-averaged sound level |

**Biological relevance**: Animal vocalizations create distinct temporal patterns. High temporal variance might indicate active calling periods, while specific skewness patterns could reflect different calling behaviors.

### Frequency Domain Indices  
Analyze spectral characteristics of the soundscape.

| Index | Full Name | What It Measures |
|-------|-----------|------------------|
| **MEANf** | Frequency Mean | Average frequency content |
| **VARf** | Frequency Variance | Spectral spread (bandwidth usage) |
| **SKEWf** | Frequency Skewness | Spectral asymmetry |
| **KURTf** | Frequency Kurtosis | Spectral concentration |
| **NBPEAKS** | Number of Peaks | Distinct frequency peaks |
| **LEQf** | Equivalent Sound Level (Frequency) | Frequency-weighted sound level |

**Biological relevance**: Different species use different frequency ranges. Marine mammals use low frequencies, fish produce mid-frequency sounds, and snapping shrimp create broadband clicks.

### Acoustic Complexity Indices
Measure overall soundscape complexity and organization.

| Index | Full Name | What It Measures |
|-------|-----------|------------------|
| **ACI** | Acoustic Complexity Index | Intensity variation across frequency bands |
| **NDSI** | Normalized Difference Soundscape Index | Balance between biological and anthropogenic sounds |
| **ADI** | Acoustic Diversity Index | Evenness of sound energy across frequencies |
| **AEI** | Acoustic Evenness Index | Uniformity of spectral energy distribution |

**Biological relevance**: High complexity often indicates active biological communities. The NDSI specifically attempts to separate biological activity from anthropogenic noise.

### Diversity Indices
Apply ecological diversity concepts to acoustic data.

| Index | Full Name | What It Measures |
|-------|-----------|------------------|
| **H_Havrda** | Havrda-Charvat Entropy | Information-theoretic diversity |
| **H_Renyi** | Renyi Entropy | Parameterized diversity measure |
| **H_pairedShannon** | Paired Shannon Diversity | Shannon diversity between frequency bands |
| **RAOQ** | Rao's Q Diversity | Functional diversity considering spectral distance |

**Biological relevance**: These indices treat frequency bands like species in ecological diversity calculations. Higher acoustic diversity may correlate with higher species diversity.

### Bioacoustic Activity Indices
Attempt to separate biological from anthropogenic sounds.

| Index | Full Name | What It Measures |
|-------|-----------|------------------|
| **BioEnergy** | Biological Energy | Energy attributed to biological sources |
| **AnthroEnergy** | Anthropogenic Energy | Energy from human-generated noise |
| **BI** | Bioacoustic Index | Ratio of mid-frequency energy (biological activity) |
| **rBA** | Relative Bioacoustic Activity | Normalized biological activity measure |

**Biological relevance**: These indices specifically target the frequency ranges and temporal patterns typical of biological sounds while filtering out vessel noise, chain sounds, and other anthropogenic sources.

### Spectral Coverage Indices
Measure how sound energy is distributed across frequency ranges.

| Index | Full Name | What It Measures |
|-------|-----------|------------------|
| **LFC** | Low Frequency Coverage | Energy in low frequency bands |
| **MFC** | Mid Frequency Coverage | Energy in mid frequency bands |
| **HFC** | High Frequency Coverage | Energy in high frequency bands |

**Biological relevance**: Different frequency bands correspond to different types of marine life:
- **Low frequencies (LFC)**: Marine mammals, large fish  
- **Mid frequencies (MFC)**: Most fish vocalizations
- **High frequencies (HFC)**: Crustacean activity (snapping shrimp)

## Research Applications

### Primary Question: Which Indices Matter?
With 56+ indices available, our analysis identifies which ones actually predict species presence. This reduces computational cost and focuses monitoring efforts on the most informative metrics.

### Index Selection Strategy
1. **PCA Analysis**: Group correlated indices to identify underlying patterns
2. **Species Correlation**: Test which indices correlate with manual species detections  
3. **Environmental Correction**: Account for temperature/depth effects on indices
4. **Validation**: Confirm index performance across stations and time periods

## Interpretation Guidelines

### High Index Values May Indicate:
- **Temporal indices**: Active calling periods, diverse activity patterns
- **Frequency indices**: Broad spectrum usage, multiple species present
- **Complexity indices**: Rich biological communities, organized soundscapes
- **Diversity indices**: Multiple simultaneous sound sources
- **Bioacoustic indices**: Biological activity rather than anthropogenic noise

### Low Index Values May Indicate:
- **Quiet periods**: Low biological activity or masking by anthropogenic noise
- **Dominant single sounds**: Vessel noise overwhelming biological sounds
- **Environmental effects**: Weather or equipment issues affecting recordings

### Important Caveats:
- Indices respond to **acoustic activity**, not necessarily **species diversity**
- A single loud species can dominate multiple indices
- Environmental factors (temperature, depth) may drive index patterns independent of biology
- Anthropogenic noise can inflate some indices while masking biological signals

## Marine Environment Considerations

### Unique Challenges:
- **Vessel noise**: Low-frequency masking of marine mammal calls
- **Chain/anchor noise**: Broadband interference from moorings
- **Snapping shrimp**: Can dominate high-frequency indices
- **Depth effects**: Sound propagation varies with depth and temperature

### Station-Specific Patterns:
- **9M, 14M, 37M**: Different distances from river mouth and marina
- **Anthropogenic exposure**: Varying levels of boat traffic
- **Habitat differences**: Depth, substrate, flow patterns affect communities

This acoustic index framework provides the foundation for automated biodiversity assessment, with the goal of identifying cost-effective alternatives to labor-intensive manual annotation methods.