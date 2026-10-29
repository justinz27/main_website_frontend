<script lang="ts">
    import CPMSOC_Logo from '$lib/assets/CPMSoc_Logo_With_Text_Baked.svg';
    import DiscordLogo from '$lib/assets/navigation/Discord_Logo.svg';
    import FacebookLogo from '$lib/assets/navigation/Facebook_Logo.svg';
    import InstagramLogo from '$lib/assets/navigation/Instagram_Logo.svg';

    const links = [
        {
            title: "Resources",
            items: [
                { name: "Blog", href: "/blog" },
                { name: "CP101", href: "/cp101" },
                { name: "CM101", href: "/cm101" }
            ]
        },
        {
            title: "Competitions",
            items: [
                { name: "Workshops", href: "/workshops" },
                { name: "Competitions", href: "/competitions" }
            ]
        },
        {
            title: "About Us",
            items: [
                { name: "Contact", href: "/contact" },
                { name: "Constitution", href: "/constitution" },
                { name: "Grievances", href: "/grievances" },
                { name: "Sponsors", href: "/sponsors" }
            ]
        }
    ];
</script>

<footer class="w-full bg-[#f8f8f8] text-black font-mono pt-8 pb-8 px-6 md:px-10">

    <div class="w-full h-px bg-black/20 mb-8"></div>

    <div class="flex flex-col lg:flex-row justify-between lg:gap-8 mb-8 px-10">

        <div class="flex flex-col gap-6 shrink-0 justify-center items-center">
            <a href="/" class="block">
                <img src={CPMSOC_Logo} alt="CPMSoc Logo" class="h-16 w-auto object-contain" />
            </a>

            <div class="flex items-center gap-4">
                <a href="https://www.facebook.com/CPMSoc/" target="_blank" rel="noreferrer" class="hover:opacity-70 transition-opacity">
                    <img src={FacebookLogo} alt="Facebook" class="size-8" />
                </a>
                <a href="https://www.instagram.com/cpmsoc_unsw/" target="_blank" rel="noreferrer" class="hover:opacity-70 transition-opacity">
                    <img src={InstagramLogo} alt="Instagram" class="size-8" />
                </a>
                <a href="https://discord.com/invite/9uxgxHY3pP" target="_blank" rel="noreferrer" class="hover:opacity-70 transition-opacity">
                    <img src={DiscordLogo} alt="Discord" class="size-8" />
                </a>
            </div>
        </div>

        <div class="flex flex-col lg:flex-row gap-8 lg:gap-20 w-full lg:w-auto">

            <div class="flex flex-col">
                <a href="/" class="hidden lg:block text-lg font-bold hover:underline">Home</a>
            </div>

            {#each links as column}
                <div class="hidden lg:block flex-col border-b border-black/10 lg:border-none">

                    <div class="hidden lg:block">
                        <h3 class="text-lg font-bold mb-4">{column.title}</h3>
                        <ul class="flex flex-col gap-3">
                            {#each column.items as link}
                                <li>
                                    <a href={link.href} class="hover:underline opacity-80 hover:opacity-100 transition-opacity">
                                        {link.name}
                                    </a>
                                </li>
                            {/each}
                        </ul>
                    </div>
                </div>
            {/each}
        </div>
    </div>

    <div class="w-full h-px bg-black/20 mb-8"></div>

    <div class="text-center text-xs opacity-60 space-y-1">
        <p>Website by CPMSoc Infrastructure. See credits <a href="/credits" class="hover:underline"> here</a>.</p>
        <p class="mt-2">© 2026 UNSW Competitive Programming and Mathematics Society</p>
    </div>
</footer>