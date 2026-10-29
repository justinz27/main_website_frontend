import { redirect } from '@sveltejs/kit';

export const load = () => {
    return redirect(302, 'https://forms.gle/ag2hKjmRojqcXGys7');
};
