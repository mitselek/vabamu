# Kiri: Küsimus isikute registri kohta

**Kuupäev**: 15. detsember 2025, 17:45  
**Saatja**: Liisi Ploom <liisi.ploom@vabamu.ee>  
**Saaja**: Mihkel Putrinš  
**Teema**: Person registry täitmise küsimus

## Sisu

```text
Tere! Saame me siinpool nüüd õigesti aru, et person_registry fail tahab
muis_participant_id asemele unikaalset koodi, jah? Meil andmekandeks
rohkem tarvis pole, kui nn donator= annetaja. Seega ma eeldan, et piisab,
kui need täidaksime? Muus osas saaksime RIKi tarvis kasutada neid siis,
kui mass-kirjeldamise võimekus muisi tekiks ja saaksime sündmusesse need
lisada.

Lasin praegu üle lugeda süsteemil ja ta väidab, et unikaalseid "annetaja
koode" võiks tulla 804?

Liisi Ploom
Peavarahoidja/Head of Collections
```

## Küsimused

1. **muis_participant_id täitmine**: Kas piisab ainult donator-välja täitmisest?
2. **Annetajate arv**: Süsteem näitab 804 unikaalset annetajat
   - Erinevus person_registry'st: 2,440 entiteeti vs 804 annetajat
   - Selgitus: person_registry sisaldab ka autor, represseeritu_o, represseeritu_t

## Kontekst

Person_registry_request.xlsx sisaldab 4 välja:

- `donator` - annetajad (804 unikaalset)
- `autor` - autorid/loojad
- `represseeritu_o` - represseeritud isikud (ohvrid)
- `represseeritu_t` - represseeritud isikud (seotud)

**Järeldus**: Kui MuIS-is vaja ainult annetajaid, siis 804 on õige number.

## Vajalik tegevus

- [ ] Vastata Liisile: kas filtreerida person_registry ainult donator-väljale?
- [ ] Või jätta kõik 2,440 entiteeti (tuleviku tarbeks RIK mass-kirjeldamine)?
