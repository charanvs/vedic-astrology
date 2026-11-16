# Matching Ruleset: `muhurta_chintamani_joshi_v1`

## Source policy

The selected North Indian convention follows Daivajna Rama's *Muhurta Chintamani*, Vivaha Prakarana verses 21–37, using the Piyushadhara commentary and Kedar Datt Joshi's Hindi charts, pp. 329–355. Six tables agree with Nemichandra Shastri's *Bharatiya Jyotish* (1970), chapter 5, pp. 608–617. Animal symbols, friendships, and Nadi groups were cross-checked against B. V. Raman's *Muhurtha* (1948), pp. 82–92. The accessible [method transcription and source notes](https://thetelugucalendar.com/marriage-matching/method/) identify the scans and page numbers.

Vashya and Yoni differ across published traditions. This release consistently uses the Muhurta Chintamani charts. It does not combine the alternate degree-split Vashya table from Bharatiya Jyotish. The Yoni chart applies two source-documented corrections: Horse/Buffalo is 0, and Mongoose-bride/Monkey-groom is 2.

## Sign classifications

| Rashi | Varna | Vashya | Lord |
|---|---|---|---|
| Mesha | Kshatriya | Chatushpada | Mars |
| Vrishabha | Vaishya | Chatushpada | Venus |
| Mithuna | Shudra | Dvipada | Mercury |
| Karka | Brahmin | Jalachara | Moon |
| Simha | Kshatriya | Chatushpada | Sun |
| Kanya | Vaishya | Dvipada | Mercury |
| Tula | Shudra | Dvipada | Venus |
| Vrischika | Brahmin | Keeta | Mars |
| Dhanu | Kshatriya | Chatushpada | Jupiter |
| Makara | Vaishya | Jalachara | Saturn |
| Kumbha | Shudra | Jalachara | Saturn |
| Meena | Brahmin | Jalachara | Jupiter |

Varna scores 1 when the groom role has an equal or higher table rank than the bride role; otherwise 0. These are symbolic categories, not caste or social identity.

## Vashya matrix

Bride rows, groom columns:

| Bride \ Groom | Dvipada | Chatushpada | Jalachara | Keeta |
|---|---:|---:|---:|---:|
| Dvipada | 2 | 0.5 | 0.5 | 1 |
| Chatushpada | 0.5 | 2 | 2 | 2 |
| Jalachara | 0.5 | 2 | 2 | 2 |
| Keeta | 1 | 2 | 2 | 2 |

## Nakshatra classifications

| Nakshatra | Yoni | Gana | Nadi |
|---|---|---|---|
| Ashwini | Horse | Deva | Adi |
| Bharani | Elephant | Manushya | Madhya |
| Krittika | Sheep | Rakshasa | Antya |
| Rohini | Serpent | Manushya | Antya |
| Mrigashira | Serpent | Deva | Madhya |
| Ardra | Dog | Manushya | Adi |
| Punarvasu | Cat | Deva | Adi |
| Pushya | Sheep | Deva | Madhya |
| Ashlesha | Cat | Rakshasa | Antya |
| Magha | Rat | Rakshasa | Antya |
| Purva Phalguni | Rat | Manushya | Madhya |
| Uttara Phalguni | Cow | Manushya | Adi |
| Hasta | Buffalo | Deva | Adi |
| Chitra | Tiger | Rakshasa | Madhya |
| Swati | Buffalo | Deva | Antya |
| Vishakha | Tiger | Rakshasa | Antya |
| Anuradha | Deer | Deva | Madhya |
| Jyeshtha | Deer | Rakshasa | Adi |
| Mula | Dog | Rakshasa | Adi |
| Purva Ashadha | Monkey | Manushya | Madhya |
| Uttara Ashadha | Mongoose | Manushya | Antya |
| Shravana | Monkey | Deva | Antya |
| Dhanishta | Lion | Rakshasa | Madhya |
| Shatabhisha | Horse | Rakshasa | Adi |
| Purva Bhadrapada | Lion | Manushya | Adi |
| Uttara Bhadrapada | Cow | Manushya | Madhya |
| Revati | Elephant | Deva | Antya |

## Tara

Count inclusively from bride Nakshatra to groom and back. Reduce each count modulo nine, with zero represented as nine. Categories 1–9 are Janma, Sampat, Vipat, Kshema, Pratyari, Sadhaka, Vadha, Maitra, and Parama Maitra. Each direction scores 0 for 3, 5, or 7 and 1.5 otherwise; maximum 3.

## Yoni matrix

Order: Horse, Elephant, Sheep, Serpent, Dog, Cat, Rat, Cow, Buffalo, Tiger, Deer, Monkey, Mongoose, Lion. Bride rows and groom columns:

```text
4 2 3 2 2 3 3 3 0 1 3 2 2 1
2 4 3 2 2 3 3 3 3 2 2 2 2 0
3 3 4 3 2 3 1 3 3 1 3 0 3 1
2 2 3 4 2 2 1 1 2 2 2 2 0 2
2 2 2 2 4 1 1 2 2 1 0 2 2 1
2 2 3 2 1 4 0 2 2 1 2 2 2 2
2 2 2 1 1 0 4 2 2 2 2 2 2 1
3 2 3 1 2 2 2 4 3 0 3 2 3 1
0 3 3 2 2 2 2 3 4 1 2 2 2 3
1 2 1 2 1 1 2 0 1 4 2 1 2 2
3 2 3 2 0 2 2 3 2 1 4 2 2 2
2 3 0 2 2 2 2 2 2 1 2 4 2 3
2 2 3 0 2 2 2 3 2 2 2 2 4 2
1 0 1 2 1 2 1 1 3 2 2 2 2 4
```

Values classify same 4, friendly 3, neutral 2, enemy 1, and great enemy 0.

## Graha Maitri matrix

Order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn. Bride rows and groom columns:

```text
5 5 5 4   5   0   0
5 5 4 1   4   0.5 0.5
5 4 5 0.5 5   3   0.5
4 1 0.5 5 0.5 5   4
5 4 5 0.5 5   0.5 3
0 0.5 3 5 0.5 5   5
0 0.5 0.5 4 3 5   5
```

## Gana matrix

Bride rows, groom columns:

| Bride \ Groom | Deva | Manushya | Rakshasa |
|---|---:|---:|---:|
| Deva | 6 | 5 | 1 |
| Manushya | 6 | 6 | 0 |
| Rakshasa | 0 | 0 | 6 |

The labels are symbolic and do not describe moral worth.

## Bhakoot and Nadi

Inclusive cyclic Rashi relationships 2/12, 5/9, and 6/8 score 0 of 7; 1/1, 3/11, 4/10, and 7/7 score 7. Same Nadi scores 0 of 8; different Nadi scores 8.

Muhurta Chintamani documents some exceptions, but this version identifies base observations only and never modifies the score. Gana exceptions requiring Navamsha lords are outside Step 10.
