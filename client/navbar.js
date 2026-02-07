document.addEventListener("DOMContentLoaded", function() {
    const role = localStorage.getItem("role") || "guest";
    const username = localStorage.getItem("username") || "";

    const navbarHTML = `
        <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <a href="all_promises.html" class="text-2xl font-bold text-blue-700 tracking-tight flex items-center gap-2">
                            🏛️ ThaiPolitics
                        </a>
                        
                        <div class="hidden md:flex ml-10 space-x-8">
                            <a href="all_promises.html" class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition">
                                รวมคำสัญญา
                            </a>
                            <a href="politicians.html" class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition">
                                ทำเนียบนักการเมือง
                            </a>
                            
                            <a href="add_update.html" id="admin-link" class="${role === 'admin' ? 'flex' : 'hidden'} items-center text-red-600 hover:text-red-800 px-3 py-2 rounded-md text-sm font-bold transition bg-red-50 hover:bg-red-100 border border-red-200">
                                ⚡ Admin Update
                            </a>
                        </div>
                    </div>

                    <div class="flex items-center gap-4">
                        ${username ? 
                            `<div class="text-right hidden sm:block">
                                <div class="text-sm font-bold text-gray-800">${username}</div>
                                <div class="text-xs text-gray-500 uppercase">${role}</div>
                            </div>
                            <button onclick="logout()" class="text-sm text-red-500 hover:text-white hover:bg-red-500 border border-red-500 px-3 py-1.5 rounded transition">
                                Logout
                            </button>` 
                            : 
                            `<a href="login.html" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-full text-sm font-medium shadow-md transition transform hover:-translate-y-0.5">
                                เข้าสู่ระบบ
                            </a>`
                        }
                    </div>
                </div>
            </div>
        </nav>
    `;

    document.getElementById("navbar-container").innerHTML = navbarHTML;
});

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}