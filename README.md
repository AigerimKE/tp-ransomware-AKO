# tp-ransomware-AKO

## Q1. Quelle est le nom de l'algorithme de chiffrement ? Est-il robuste et pourquoi ?

C'est l'algorithme de *chiffrement symmetrique*. 

Comme le système de chiffrement symétrique utilise la même clé pour le cryptage et le décryptage, l'expéditeur et le destinataire doivent connaître la clé avant d'échanger des messages. Le processus est généralement plus rapide dans les chiffrements symétriques en raison de la longueur réduite des clés. L'inconvénient de ce système est que les expéditeurs et les destinataires doivent échanger des clés avant de décrypter le message. Si les clés ne sont pas changées régulièrement, le système sera sujet à des attaques puisqu'un attaquant peut utiliser la clé divulguée pour perturber la communication.

---

## Q2. Pourquoi ne pas hacher le sel et la clef directement ? Et avec un hmac ?

Il faut les passer par la derivation avec plusieurs iterations pour bien hacher les deux constants aléatoires cryptographiques(qui sont quasi aléatoires). 
Le fait de les dérivé séparament ajoute plus du temps pour l'exécution d'attaque.
Et hmac est utilisé pour vérifier l'integralité des données.

---

## Q3. Pourquoi il est préférable de vérifier qu'un fichier token.bin n'est pas déjà présent ?

Pour ne pas écraser le token s'il existe. Car si on réécrit le token.bin avant d'utiliser pour le decryptage, on peut perdre la bonne clef qui correspond à ce token qu'on a écraser.

---

## Q4. Comment vérifier que la clef la bonne ?

On peut vérifier la clef en l'envoyant vers le cnc et en la décodant de la base64. On peut faire une condition avec raise si ça ne convient pas.

