/* Huiying Int'l Business Co. — product category data (EN) */

const SERIES = [
  {
    id: 'primer',
    name: 'Waterproofing Primers',
    tagline: 'Substrate sealing and adhesion',
    desc: 'Single-component water-based primers used to seal and consolidate the substrate and to strengthen adhesion of the waterproofing layer above. Film-forming, fast-drying penetrating, multi-purpose reinforcing and inorganic types are available for new or aged concrete, friable surfaces and chalked substrates.',
    feat: [
      'Water-based, no solvent odour, no fire hazard in handling',
      'Fast drying with good penetration; no residual tack once cured',
      'Strong adhesion to concrete; improves impact resistance',
      'Dense, water-resistant film that prevents surface chalking'
    ],
    use: 'Priming for roof, wall, bathroom and kitchen sandwich waterproofing; bonding coat for external walls, courtyards and basement retaining walls',
    spec: [['Coverage', 'approx. 0.05–0.1 kg/m² per coat'], ['Packaging', '16–18 kg']]
  },
  {
    id: 'compound',
    name: 'Compound Membrane Systems',
    tagline: 'Main waterproofing layer',
    desc: 'Single-component membranes based on water-based polymer resins with aggregate or anti-crack fibre, curing to a continuous elastic film. Acrylic fibre-reinforced, high-elasticity, high-elongation, chloroprene-polyurethane, bituminous emulsion and water-based polyurethane types are available.',
    feat: [
      'Elongation from 400% to 1500% depending on type',
      'Single-component and water-based; ready to use from the pail',
      'Tested for tensile and peel strength',
      'Weather resistant, odourless and non-toxic; avoids the hydrolysis issues of cement-based heavy-build systems'
    ],
    use: 'Roofs, external walls, floor junctions, window perimeters, terraces and balconies; bathroom and kitchen sandwich waterproofing; basement retaining walls',
    spec: [['Coverage', 'approx. 0.4–2.0 kg/m² depending on type and number of coats'], ['Packaging', '18–20 kg']]
  },
  {
    id: 'topcoat',
    name: 'Topcoats',
    tagline: 'Protection and thermal reflection',
    desc: 'Applied over the waterproofing layer to provide finish, UV protection and thermal insulation. Reflective thermal topcoats (65%+ reflectance), elastomeric topcoats and water-based polyurethane finishes are available in a range of colours.',
    feat: [
      'Reflective type achieves 65%+ solar reflectance, lowering internal temperature and cooling load',
      'Elastic, flexible film that moves with the substrate without cracking',
      'Weather and mould resistant; colour stable over time',
      'Available in white, grey, beige, green and off-white'
    ],
    use: 'External wall finishes; metal roofs, corrugated sheeting, steel panels and container units; roof membrane finish coats',
    spec: [['Coverage', 'approx. 0.2–0.8 kg/m²'], ['Packaging', '18 kg']]
  },
  {
    id: 'cement',
    name: 'Flexible Cement',
    tagline: 'Two-part resin and aggregate systems',
    desc: 'Two-component systems combining a water-based resin with selected inorganic aggregate, curing to a tough film that is both elastic and high in strength. Standard, copolymer emulsion, heavy-build (up to 3 mm in one pass) and vinyl resin types are available, along with pressure-sensitive adhesive and injection grades.',
    feat: [
      'Excellent adhesion to concrete; elastic and crack-resistant film',
      'Heavy-build type achieves 3 mm in a single application without delamination',
      'Water-based with no solvent odour',
      'Compatible with elastomeric or thermal topcoats as a finish layer'
    ],
    use: 'External walls, roofs, bathrooms and courtyards; internal-layer waterproofing to basement retaining walls',
    spec: [['Coverage', 'approx. 1.0–1.2 kg/m² horizontal, 0.6–0.8 kg/m² vertical, per coat'], ['Packaging', 'resin 18 kg + aggregate']]
  },
  {
    id: 'silicate',
    name: 'Plugging and Crystalline Systems',
    tagline: 'Remedial treatment for active leaks',
    desc: 'Hydraulic cement-based compounds. Rapid-set plugging mortar cures in 3–5 minutes and immediately stops water ingress through cracks and honeycombing. Crystalline penetrating grades react with the concrete to form crystals that seal pores and micro-cracks, and can be applied to damp surfaces.',
    feat: [
      'Plugging mortar stops water instantly and will cure under water',
      'No shrinkage after curing; high structural strength',
      'Contains no metallic constituents; will not rust or expand',
      'Crystalline grades remain vapour permeable and protect reinforcement from corrosion'
    ],
    use: 'Leaking cracks in concrete or masonry; surface defect and exposed-reinforcement repair; anchor fixing; sealing around pipe penetrations',
    spec: [['Reference usage', '1 kg plugging mortar fills approx. 600 cm³; crystalline grade approx. 1.0 kg/m² per mm thickness'], ['Packaging', '16–20 kg']]
  },
  {
    id: 'clear',
    name: 'Clear Protective Coatings',
    tagline: 'Stain and weather resistance',
    desc: 'Transparent protective layers applied over topcoats or decorative finishes to improve stain and weather resistance. Gloss, matt (5–10 GU) and two-component water-based matt or gloss grades are available, along with a solvent-based non-yellowing finish.',
    feat: [
      'Hydrophobic, dust-shedding film with self-cleaning behaviour',
      'Resistant to acid, alkali and weathering; protects the decorative layer from colour change',
      'Available in gloss and matt finishes',
      'Non-yellowing grade leaves the original appearance of the building unchanged'
    ],
    use: 'Protection of coated surfaces, exposed aggregate, power-floated cement, board materials and tiling; internal and external walls and trim',
    spec: [['Coverage', 'approx. 0.05–0.1 kg/m²'], ['Packaging', '15–18 kg']]
  },
  {
    id: 'oil',
    name: 'Solvent-Based PU Systems',
    tagline: 'Two-part polyurethane',
    desc: 'Two-component polyurethane waterproofing systems offering toughness, elasticity and reliable resistance to water ingress. The range covers membrane, elastomeric topcoat, thermal layer and non-sag joint sealant, and can be used with a single-component PU primer.',
    feat: [
      'High tensile strength and elongation; resistant to acid, alkali and weathering',
      'Thermal grade reflects approximately 65% of solar radiation',
      'Non-sag sealant suits both vertical and horizontal joints',
      'Primer bonds strongly to cementitious substrates and to PU'
    ],
    use: 'Roof waterproofing and thermal protection for high-rise buildings, factories, car parks and apartment blocks; roof gardens, basements, bathrooms and swimming pools; movement joints',
    spec: [['Coverage', 'membrane approx. 2.6–3.9 kg/m², topcoat approx. 0.2–0.4 kg/m²'], ['Packaging', 'base 10–20 kg + hardener 5–10 kg']]
  }
];

const STONE_SYSTEM = [
  { step: '1', name: 'Substrate preparation', desc: 'Clean the surface, remove contaminants, dust and loose material; leave dry and smooth', tool: '—', qty: '—', gap: '—' },
  { step: '2', name: 'Joint setting out', desc: 'Set out joints to the design drawing with a chalk line; mask with tape to the required joint width', tool: '—', qty: '—', gap: '—' },
  { step: '3', name: 'Levelling', desc: 'Proprietary levelling putty applied to a standard rendered finish; substrate flatness within 2 mm', tool: 'Trowel, scraper', qty: '2 coats', gap: '8H min.' },
  { step: '4', name: 'Primer', desc: 'Penetrating sealer primer to seal the substrate and retain curing moisture', tool: 'Roller, spray', qty: '0.1–0.15 kg/m²', gap: '4H min.' },
  { step: '5', name: 'Joints', desc: 'Applied in the colour specified by the design and client; masked with tape', tool: '—', qty: '—', gap: '—' },
  { step: '6', name: 'Base coat', desc: 'Pigmented base coat, thinned with 3%–5% water', tool: 'Roller, spray', qty: '0.2–0.3 kg/m² (1–2 coats)', gap: '8H min.' },
  { step: '7', name: 'Stone-effect coating', desc: 'Main stone-effect material, thinned with 5%–10% water', tool: 'Dedicated spray gun', qty: '0.9–1.2 kg/m² (1–2 coats)', gap: '24H min.' },
  { step: '8', name: 'Joint reveal', desc: 'Remove masking tape immediately after spraying to reveal the joints', tool: '—', qty: '—', gap: '—' },
  { step: '9', name: 'Protective coat', desc: 'Clear topcoat, thinned with 10%–20% water', tool: 'Dedicated spray gun', qty: '0.1–0.15 kg/m² (1 coat)', gap: '12H min.' }
];

const STONE_PRODUCTS = [
  {
    name: 'Penetrating Sealer Primer',
    desc: 'A high-polymer acrylic copolymer resin emulsion classed as a specialist waterproofing material. Once cured over the levelling layer it forms a dense film that slows moisture loss and maintains good curing conditions. Suitable over natural stone, aggregate, limestone, cementitious surfaces, concrete, render and firebrick.',
    feat: ['Fast drying with high penetration', 'Bonds in both directions; alkali and water resistant', 'Water-based, safe and non-toxic', 'Particularly suited to under-cured levelling layers'],
    qty: '0.1–0.15 kg/m²', pack: '18 kg / pail'
  },
  {
    name: 'Pigmented Base Coat',
    desc: 'A single-component coating of water-based polymer and selected pigment, ready to use from the pail. Good workability, cures directly after roller application, and forms an elastic, high-strength, durable film with a high sheen.',
    feat: ['Improves opacity', 'High penetration and sealing capability', 'Strong adhesion to cementitious surfaces', 'Suits alkali sealing on new and existing high-end substrates'],
    qty: '0.2–0.3 kg/m²', pack: '18 kg / pail'
  },
  {
    name: 'Stone-Effect Coating',
    desc: 'Produced using an advanced granulation process, a single product contains five or more distinct colour particles. Sprayed in one pass, the particles merge into a film reproducing the appearance of natural granite, with genuine relief, a coarse tactile finish and rich colour.',
    feat: ['Over 90% visual match to natural granite', 'Tightly controlled particle size and colour consistency', 'Reproduces the natural veining and texture of high-grade stone', 'Dense, hard film with water and alkali resistance'],
    qty: '0.9–1.2 kg/m²', pack: '20 kg / pail'
  },
  {
    name: 'Clear Topcoat',
    desc: 'A water-based acrylic resin synthesised with silane and nano technology, forming a dense, transparent and tough film. Durable against weathering, water and staining, easy to wash down, and gives lasting protection to the coating below.',
    feat: ['Improves stain and weather resistance of the coloured layer', 'Balanced hydrophobic and oleophobic behaviour with excellent self-cleaning', 'Excellent resistance to water whitening', 'Available in gloss or matt to suit the design'],
    qty: '0.1–0.15 kg/m²', pack: '18 kg / pail'
  },
  {
    name: 'Joint Coating',
    desc: 'A dedicated coating for setting out joints within the stone-effect system. Divides the elevation into panels of the specified shape and size, improving both the realism of the finish and the overall composition of the facade. Formulated from pure acrylic copolymer resin with high-durability titanium dioxide and imported pigment.',
    feat: ['Improves the realism of the stone-effect finish', 'Excellent adhesion and opacity', 'Outstanding weathering, water and alkali resistance', 'Flexible and crack resistant; water-based; colour to order'],
    qty: '0.20–1.30 kg/m²', pack: '18 kg / pail'
  }
];

const STONE_SWATCHES = [
  { file: 'stone-01', code: 'HY-101', name: 'Pearl White' },
  { file: 'stone-02', code: 'HY-102', name: 'Sesame Grey' },
  { file: 'stone-03', code: 'HY-103', name: 'Deep Sea Grey' },
  { file: 'stone-04', code: 'HY-104', name: 'Ivory White' },
  { file: 'stone-05', code: 'HY-105', name: 'Rose Red' },
  { file: 'stone-06', code: 'HY-201', name: 'Snow White' },
  { file: 'stone-07', code: 'HY-202', name: 'Light Speckle' },
  { file: 'stone-08', code: 'HY-203', name: 'Bluestone Grey' },
  { file: 'stone-09', code: 'HY-204', name: 'Warm Sand' },
  { file: 'stone-10', code: 'HY-205', name: 'Ochre Speckle' },
  { file: 'stone-11', code: 'HY-301', name: 'Salt and Pepper' },
  { file: 'stone-12', code: 'HY-302', name: 'Crystal White' },
  { file: 'stone-13', code: 'HY-303', name: 'Iron Grey' },
  { file: 'stone-14', code: 'HY-304', name: 'Beige Speckle' },
  { file: 'stone-15', code: 'HY-305', name: 'Blue Rust' }
];

const EPOXY_SYSTEMS = [
  ['Primer coating system', 'Penetrates and seals the substrate, improving adhesion and hardness as the first layer of the build-up', 'All cementitious substrates'],
  ['Body coat system', 'Acts as the structural layer, improving flatness, thickness, mechanical strength and impact resistance while reducing overall material cost', 'Factories and warehousing'],
  ['Thin-build topcoat system', 'Easy to apply, attractive finish, wide colour choice, convenient installation; prevents dusting', 'Car parks, factories, garages'],
  ['Self-levelling system', 'Excellent adhesion, smooth surface, good water and chemical resistance, high gloss', 'Hospitals, pharmaceutical and electronics plants, food factories, cleanrooms, schools, offices'],
  ['Clear topcoat system', 'Forms a protective layer over the floor with high gloss, transparency, strength and chemical resistance', 'Hotels, residential, design studios, offices, pharmaceutical and food facilities'],
  ['Anti-static system', 'Dissipates static charge accumulating at the floor surface, preventing sparking', 'Semiconductor and electronics plants, computer rooms, hazardous areas, instrument facilities'],
  ['Water-based system', 'Environmentally responsible flooring with no VOC, low odour, good appearance and cure characteristics', 'Food, electronics, pharmaceutical, cosmetics and paper plants'],
  ['Structural repair products', 'Materials for structural repair and strengthening', 'Refurbishment works']
];
