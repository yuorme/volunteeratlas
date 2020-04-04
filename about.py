import dash_core_components as dcc

def get_about_text(language):
    '''Generate markdown for the About Us section in a given language
    Currently supports 'en' and 'fr'
    '''

    en_text = '''
    ##### Our Mission

    Welcome to Volunteer Atlas, an interactive map connecting healthy volunteers with people in need of deliveries during COVID-19 (and beyond)!

    Feeling helpless in the face of this international emergency, have extra time and want to help safely deliver supplies to those in need? Sign up as a volunteer and connect with others in your community who could greatly benefit from your support. We just need to collect a bit of information from you to begin.

    If you or someone you know is self-isolating, immunocompromised, vulnerable, or elderly and needs help picking up groceries, running errands, or grabbing other supplies, have a look at the volunteers available in your neighbourhood and contact someone directly. All the volunteers’ identities have been verified and you can read a bit about each one to choose someone you feel comfortable with. 

    The goal of this project is to create long-term mutual aid partnerships in our communities - connecting volunteers and beneficiaries in each area to strengthen these networks now and beyond the COVID crisis. We hope to use this crisis as an opportunity to build resilience in our communities, putting in place the safeholds that will keep us stronger and more interdependent in the future.

    We are also looking to connect with other mutual aid groups, food banks, meals on wheels programs, etc to create a more centralized system that will facilitate deliveries through all these networks. If your organization is looking for volunteers or needs help organizing deliveries, please don’t hesitate to get in touch and we will be happy to collaborate!

    ##### Privacy
    We take your privacy seriously. Only your **Given Name**, **Email Address** and **About Me** sections will be shared on the publicly if you sign up as a volunteer. No personal information will be displayed for those requesting deliveries to protect the identities of the vulnerable. All additional personal information will only be accessible by admins and will be used solely to confirm identities and protect those we are seeking to help. 
    
    Our system is also designed to protect your physical location. We only ask for a postal code (not your home address) to get your approximate location. We then add an additional 500m of random noise to further protect your privacy.

    ##### FAQs
    **Why might posting my information on this website be more helpful than just posting on Facebook/Twitter?**

    Vulnerable people needing help the most are likely those who do not live in the same city as their close relatives/friends. Close relatives who live outside of the locality are less likely to see or be aware of Facebook groups or Twitter posts from localized help groups. Also, social media is ephemeral, if you are offering to help over a course of weeks or months, putting your information into a central repository is a more effective way to do it.

    **What is the process for connecting volunteers with recipients?**

    Your approximate location will populate an interactive map and certain details from your responses will be available on your 'public profile'. Recipients will navigate through the map to select the most suitable volunteer based on their profile. A small group of admin will be involved in facilitating your volunteer effort behind the scenes.

    **Buying groceries for more than just yourself might look to others like panic buying. What can I do if I'm confronted/prevented from shopping based on such suspicions?**

    We are thinking about ways to implement a verification and authentication program. For the time being, we recommend you speak with store staff/management about your volunteerism and show them your registration on this website.
    '''

    fr_text = '''
    ##### Notre Objectif
    Bienvenue à VolunteerAtlas, un projet géographique qui met en relation des bénévoles en bonne santé avec des personnes ayant besoin d'aide avec leurs courses pendant COVID-19 (et au-delà) ! Vous vous sentez impuissant face à cette urgence internationale, vous avez plus de temps libre ces temps-ci et vous voulez aider des personnes dans le besoin à procurer des provisions en toute sécurité ? Inscrivez-vous en tant que bénévole et entrez en contact avec d'autres membres de votre communauté qui pourraient grandement bénéficier de votre soutien. Nous avons simplement besoin de recueillir quelques informations vous concernant, puis c'est parti.

    Si vous ou quelqu'un que vous connaissez est en état d'auto-isolement, immunodéficient, vulnérable ou âgé et a besoin d'aide pour faire des courses ou d'autres fournitures, consultez les bénévoles disponibles dans votre quartier et prenez directement contact avec quelqu'un. L'identité de tous les bénévoles a été vérifiée et vous pouvez en apprendre davantage sur chacun d'entre eux afin de choisir une personne avec laquelle vous vous sentez à l'aise. 

    L'objectif de ce projet est de créer des partenariats d'aide mutuelle durables dans nos communautés en reliant des bénévoles et des bénéficiaires dans chaque quartier. Nous espérons utiliser cette crise comme une occasion de renforcer la résilience de nos communautés, en mettant en place les garde-fous qui nous permettront d'être plus forts et plus interdépendants à l'avenir.

    Nous cherchons également à nous connecter avec d'autres groupes d'aide mutuelle, des banques alimentaires, des programmes de repas à domicile, etc. afin de créer un système plus centralisé qui facilitera les livraisons à travers tous ces réseaux. Si votre organisme cherche des bénévoles ou a besoin d'aide pour organiser des livraisons, n'hésitez pas à nous contacter et nous serons heureux de collaborer avec vous !

    ##### Privacy
    Nous prenons votre vie privée au sérieux. Seules vos sections **Prénom**, **Adresse électronique** et **A propos de moi** seront diffusées publiquement si vous vous inscrivez en tant que volontaire. Aucune information personnelle ne sera affichée pour les personnes qui demandent des livraisons afin de protéger l'identité des personnes vulnérables. Toutes les informations personnelles supplémentaires ne seront accessibles qu'aux administrateurs et ne seront utilisées que pour confirmer les identités et protéger les personnes que nous cherchons à aider. 
    
    Notre système est également conçu pour protéger votre emplacement physique. Nous ne demandons qu'un code postal (et non votre adresse personnelle) pour obtenir votre localisation approximative. Nous ajoutons ensuite 500 mètres de bruit aléatoire pour protéger davantage votre vie privée.

    ##### FAQs
    **Pourquoi la publication de mes informations sur ce site web serait-elle plus utile qu'une simple publication sur Facebook/Twitter ?

    Les personnes vulnérables qui ont le plus besoin d'aide sont probablement celles qui ne vivent pas dans la même ville que leurs proches/amis. Les parents proches qui vivent en dehors de la localité sont moins susceptibles de voir ou d'être informés des groupes Facebook ou des messages Twitter des groupes d'aide localisés. Par ailleurs, les médias sociaux sont éphémères. Si vous proposez votre aide sur une période de plusieurs semaines ou de plusieurs mois, il est plus efficace de placer vos informations dans un dépôt central.

    **Quel est le processus de mise en relation des bénévoles avec les bénéficiaires ?

    Votre emplacement approximatif apparaîtra sur une carte interactive et certains détails de vos réponses seront disponibles sur votre "profil public". Les bénéficiaires navigueront sur la carte pour sélectionner le volontaire le plus approprié en fonction de leur profil. Un petit groupe d'administrateurs sera impliqué pour faciliter votre travail de bénévole en coulisses.

    **Acheter des produits alimentaires pour d'autres personnes que vous-même peut sembler être un acte de panique. Que puis-je faire si je suis confronté/empêché d'acheter sur la base de tels soupçons ?

    Nous réfléchissons aux moyens de mettre en place un programme de vérification et d'authentification. Pour l'instant, nous vous recommandons de parler de votre bénévolat avec le personnel/la direction du magasin et de leur montrer votre inscription sur ce site.
    '''

    if language == 'en':
        return dcc.Markdown(en_text)
    elif language == 'fr':
        return dcc.Markdown(fr_text)