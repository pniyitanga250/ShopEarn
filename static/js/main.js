// ShopEarn Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate on Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });
    
    // Initialize GSAP animations
    if (typeof gsap !== 'undefined') {
        // Hero section animations
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            gsap.from('.hero-shape', {
                opacity: 0,
                scale: 0.5,
                duration: 1.5,
                stagger: 0.3,
                ease: 'power3.out'
            });
            
            gsap.from('.hero-image', {
                opacity: 0,
                y: 50,
                duration: 1,
                delay: 0.5,
                ease: 'power3.out'
            });
            
            gsap.from('.floating-badge', {
                opacity: 0,
                scale: 0,
                duration: 0.8,
                stagger: 0.2,
                delay: 1,
                ease: 'back.out(1.7)'
            });
        }
        
        // Initialize ScrollTrigger for section animations
        if (typeof ScrollTrigger !== 'undefined') {
            // Product card animations
            gsap.utils.toArray('.product-card').forEach(card => {
                gsap.from(card, {
                    scrollTrigger: {
                        trigger: card,
                        start: 'top bottom-=100',
                        toggleActions: 'play none none none'
                    },
                    y: 50,
                    opacity: 0,
                    duration: 0.8,
                    ease: 'power3.out'
                });
            });
            
            // How it works section
            const howItWorks = document.querySelector('.how-it-works');
            if (howItWorks) {
                gsap.from('.process-step', {
                    scrollTrigger: {
                        trigger: howItWorks,
                        start: 'top center'
                    },
                    opacity: 0,
                    y: 30,
                    stagger: 0.3,
                    duration: 0.8,
                    ease: 'power3.out'
                });
                
                gsap.from('.process-connector', {
                    scrollTrigger: {
                        trigger: howItWorks,
                        start: 'top center'
                    },
                    width: 0,
                    duration: 1.5,
                    ease: 'power3.inOut'
                });
            }
            
            // MLM Benefits section
            const mlmBenefits = document.querySelector('.mlm-benefits');
            if (mlmBenefits) {
                gsap.from('.mlm-stats-card', {
                    scrollTrigger: {
                        trigger: mlmBenefits,
                        start: 'top center'
                    },
                    opacity: 0,
                    scale: 0.8,
                    stagger: 0.2,
                    duration: 0.8,
                    ease: 'back.out(1.7)'
                });
            }
            
            // Testimonials section
            const testimonials = document.querySelector('.testimonials');
            if (testimonials) {
                gsap.from('.testimonial-stat', {
                    scrollTrigger: {
                        trigger: testimonials,
                        start: 'top center'
                    },
                    opacity: 0,
                    y: 30,
                    stagger: 0.2,
                    duration: 0.8,
                    ease: 'power3.out'
                });
            }
            
            // CTA section
            const ctaSection = document.querySelector('.cta-section');
            if (ctaSection) {
                gsap.from('.cta-feature', {
                    scrollTrigger: {
                        trigger: ctaSection,
                        start: 'top center'
                    },
                    opacity: 0,
                    y: 30,
                    stagger: 0.2,
                    duration: 0.8,
                    ease: 'power3.out'
                });
            }
        }
    }
    
    // Animate counter numbers
    function animateCounter(el) {
        const target = parseInt(el.getAttribute('data-count'));
        const duration = 2000; // 2 seconds
        const step = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current < target) {
                el.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                el.textContent = target;
            }
        };
        
        updateCounter();
    }
    
    // Use Intersection Observer to trigger counter animation when visible
    const counterElements = document.querySelectorAll('[data-count]');
    if (counterElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counterElements.forEach(el => {
            observer.observe(el);
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentLocation || (href !== '/' && currentLocation.startsWith(href))) {
            link.classList.add('active');
        }
    });
    
    // Global handler for commission modals
    window.openCommissionModal = function(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modalInstance = new bootstrap.Modal(modalElement);
            modalInstance.show();
        }
        return false; // Prevent default action
    };

    // Product quantity selector
    const quantityInputs = document.querySelectorAll('.quantity-input');
    if (quantityInputs) {
        quantityInputs.forEach(function(input) {
            const minusBtn = input.previousElementSibling;
            const plusBtn = input.nextElementSibling;
            
            if (minusBtn && minusBtn.classList.contains('quantity-minus')) {
                minusBtn.addEventListener('click', function() {
                    if (input.value > 1) {
                        input.value = parseInt(input.value) - 1;
                        triggerChangeEvent(input);
                    }
                });
            }
            
            if (plusBtn && plusBtn.classList.contains('quantity-plus')) {
                plusBtn.addEventListener('click', function() {
                    input.value = parseInt(input.value) + 1;
                    triggerChangeEvent(input);
                });
            }
        });
    }

    // Helper function to trigger change event
    function triggerChangeEvent(element) {
        const event = new Event('change', { bubbles: true });
        element.dispatchEvent(event);
    }

    // Cart update form submission
    const cartUpdateForms = document.querySelectorAll('.cart-update-form');
    if (cartUpdateForms) {
        cartUpdateForms.forEach(function(form) {
            const quantityInput = form.querySelector('.quantity-input');
            if (quantityInput) {
                quantityInput.addEventListener('change', function() {
                    form.submit();
                });
            }
        });
    }

    // MLM Binary Tree Visualization - Disabled
    // Binary tree visualization has been removed

    // Commission Chart (if Chart.js is loaded)
    const commissionChartCanvas = document.getElementById('commissionChart');
    if (commissionChartCanvas && typeof Chart !== 'undefined') {
        const ctx = commissionChartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: commissionLabels || ['No Data'],
                datasets: [{
                    label: 'Commission Earnings',
                    data: commissionData || [0],
                    backgroundColor: 'rgba(78, 115, 223, 0.8)',
                    borderColor: 'rgba(78, 115, 223, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }

    // Referral link copy functionality
    const referralLinkCopy = document.getElementById('copy-referral-link');
    if (referralLinkCopy) {
        referralLinkCopy.addEventListener('click', function(e) {
            e.preventDefault();
            const referralLink = document.getElementById('referral-link');
            if (referralLink) {
                navigator.clipboard.writeText(referralLink.value).then(function() {
                    // Show success message
                    const originalText = referralLinkCopy.textContent;
                    referralLinkCopy.textContent = 'Copied!';
                    referralLinkCopy.classList.add('btn-success');
                    referralLinkCopy.classList.remove('btn-primary');
                    
                    setTimeout(function() {
                        referralLinkCopy.textContent = originalText;
                        referralLinkCopy.classList.remove('btn-success');
                        referralLinkCopy.classList.add('btn-primary');
                    }, 2000);
                });
            }
        });
    }
});