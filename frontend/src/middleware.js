import { NextResponse } from 'next/server';

export async function middleware(request) {
 const jwt = request.cookies.get('jwt');

 const response = NextResponse.next();

 if (request.nextUrl.pathname !== "/login") {
   response.cookies.delete('2fa_token');
 }

 const is2fa = request.cookies.get("2fa_token");
 if (is2fa && request.nextUrl.pathname !== "/2fa") {
   return NextResponse.redirect(new URL("/2fa", request.url));
 }

 if (request.nextUrl.pathname === "/") {
   return NextResponse.redirect(new URL('/login', request.url));
 }

 const isAuthPage = request.url.includes("/login") || request.url.includes("/signup");
 const isRoot = request.nextUrl.pathname === "/";

 if (isRoot) return response;
 if (!jwt && !isAuthPage) {
   return NextResponse.redirect(new URL('/login', request.url));
 }

 if (!isAuthPage) {
   try {
     const backendResponse = await fetch(`${process.env.NEXT_PUBLIC_URL}/backend/auth/verify`, {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
       },
       credentials: 'include',
       body: JSON.stringify({ token: jwt?.value })
     });

     if (!backendResponse.ok) {
       const redirectResponse = NextResponse.redirect(new URL('/login', request.url));
       redirectResponse.cookies.delete('jwt');
       return redirectResponse;
     }
     
     response.cookies.set('isAuth', 'true', { path: '/' });
     return response;
   } catch (error) {
     return NextResponse.redirect(new URL('/500', request.url));
   }
 }

 if (jwt && isAuthPage) {
   return NextResponse.redirect(new URL('/profile', request.url));
 }

 return response;
}

export const config = {
 matcher: [
   "/",
   "/ws/:path*",
   "/edit_profile/:path*", 
   "/settings/:path*", 
   "/dashboard/:path*",
   "/profile/:path*",
   "/game/:path*",
   "/chat/:path*",
   "/create_join_tournament/:path*",
   "/tournament_board/:path*",
   "/waiting_random_game/:path*",
   "/waiting_random_c4/:path*",
   "/connect_four/:path*",
   "/local_c4/:path*",
   "/connect_four_mode/:path*",
   "/bot/:path*",
   "/list_of_friends/:path*",
   "/mode/:path*",
   "/play/:path*",
   "/waiting_friends_game/:path*",
   "/local_game/:path*",
   "/tournament/:path*",
   "/l_game/:path*",
 ],
};