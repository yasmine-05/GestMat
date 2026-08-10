console.log("Dashboard loaded successfully");

const menuItems = document.querySelectorAll(".menu-item");

menuItems.forEach(item => {

    item.addEventListener("click", function() {

        menuItems.forEach(menu => {
            menu.classList.remove("active");
        });

        this.classList.add("active");

    });

});

const showAllButton = document.getElementById("showAllBtn");

if (showAllButton) {

    showAllButton.addEventListener("click", function() {

        alert("Tous les matériels seront affichés ici.");

    });

}