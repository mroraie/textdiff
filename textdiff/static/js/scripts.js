$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize Bootstrap tabs
    var tabElms = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabElms.forEach(function(tabEl) {
        new bootstrap.Tab(tabEl);
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        event.preventDefault();
        $('html, body').animate({
            scrollTop: $($(this).attr('href')).offset().top - 70
        }, 800);
    });

    // Textarea auto-resize
    $('textarea').each(function() {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Form submission animation
    $('form').submit(function() {
        $(this).addClass('animate__animated animate__pulse');
        setTimeout(() => {
            $(this).removeClass('animate__animated animate__pulse');
        }, 1000);
    });

    // Add ripple effect to buttons
    $('.btn').on('click', function(e) {
        var x = e.pageX - $(this).offset().left;
        var y = e.pageY - $(this).offset().top;
        
        var $ripple = $('<span class="ripple"></span>');
        $ripple.css({
            left: x,
            top: y
        });
        
        $(this).append($ripple);
        
        setTimeout(function() {
            $ripple.remove();
        }, 1000);
    });

    // Print Results
    $('#printResults').click(function() {
        window.print();
    });
    
    // Save Results (simulated)
    $('#saveResults').click(function() {
        alert('در نسخه واقعی، این گزینه نتایج را ذخیره خواهد کرد');
    });
    
    // Scroll to Top Button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $('#scrollToTop').fadeIn();
        } else {
            $('#scrollToTop').fadeOut();
        }
    });
    
    $('#scrollToTop').click(function() {
        $('html, body').animate({scrollTop: 0}, 'smooth');
        return false;
    });
    
    // Highlight table rows on hover
    $('.table-hover tbody tr').hover(
        function() {
            $(this).addClass('table-active');
        },
        function() {
            $(this).removeClass('table-active');
        }
    );
    
    // Copy buttons functionality
    function showToast() {
        var toast = new bootstrap.Toast(document.getElementById('copyToast'));
        toast.show();
    }
    
    $('.copy-btn, .copy-all').click(function() {
        var target = $(this).data('target');
        var text = $(target).text().trim();
        navigator.clipboard.writeText(text).then(showToast);
    });
    
    // Toggle text direction for phonetic
    $('.toggle-direction').click(function() {
        $('.phonetic-text').each(function() {
            var currentDir = $(this).attr('dir');
            $(this).attr('dir', currentDir === 'ltr' ? 'rtl' : 'ltr');
        });
    });
    
    // Operations search functionality
    $('.search-ops').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('.op-row').filter(function() {
            var rowText = $(this).find('.op-desc').text().toLowerCase();
            $(this).toggle(rowText.indexOf(value) > -1);
        });
    });
    
    // Animation on scroll
    function animateOnScroll() {
        $('.animate-on-scroll').each(function() {
            var position = $(this).offset().top;
            var scroll = $(window).scrollTop();
            var windowHeight = $(window).height();
            
            if (scroll + windowHeight - 100 > position) {
                var animation = $(this).data('animation') || 'fadeInUp';
                $(this).addClass('animate__animated animate__' + animation);
            }
        });
    }
    
    $(window).scroll(animateOnScroll);
    animateOnScroll(); // Run once on page load
});


$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Copy functionality
    $('.copy-btn, .copy-all').click(function() {
        let target = $(this).data('target');
        let text = $(target).text().trim();
        
        navigator.clipboard.writeText(text).then(function() {
            let toast = new bootstrap.Toast($('#copyToast'));
            toast.show();
        });
    });
    
    // Toggle text direction for phonetic comparison
    $('.toggle-direction').click(function() {
        $('.phonetic-text').each(function() {
            let currentDir = $(this).attr('dir');
            $(this).attr('dir', currentDir === 'ltr' ? 'rtl' : 'ltr');
        });
    });
    
    // Search in operations table
    $('.search-ops').on('keyup', function() {
        let value = $(this).val().toLowerCase();
        $('.ops-table tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
    
    // Print results
    $('#printResults').click(function() {
        window.print();
    });
    
    // Save results (placeholder functionality)
    $('#saveResults').click(function() {
        // In a real app, this would save to database or generate a PDF
        alert('این قابلیت در نسخه کامل پیاده‌سازی خواهد شد');
    });
    
    // Scroll to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $('#scrollToTop').fadeIn();
        } else {
            $('#scrollToTop').fadeOut();
        }
    });
    
    $('#scrollToTop').click(function() {
        $('html, body').animate({scrollTop: 0}, 'smooth');
    });
    
    // Animation on scroll
    function animateOnScroll() {
        $('.animate-on-scroll').each(function() {
            let position = $(this).offset().top;
            let scroll = $(window).scrollTop();
            let windowHeight = $(window).height();
            
            if (scroll + windowHeight - 100 > position) {
                let animation = $(this).data('animation');
                $(this).addClass('animate__animated animate__' + animation);
            }
        });
    }
    
    $(window).scroll(animateOnScroll);
    animateOnScroll(); // Run once on page load
});

$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Copy functionality
    $('.copy-btn').click(function() {
        var target = $(this).data('target');
        var text = $(target).text();
        navigator.clipboard.writeText(text);
        showToast();
    });
    
    $('.copy-all').click(function() {
        var target = $(this).data('target');
        var text = $(target).map(function() {
            return $(this).text();
        }).get().join('\n');
        navigator.clipboard.writeText(text);
        showToast();
    });
    
    function showToast() {
        var toast = new bootstrap.Toast(document.getElementById('copyToast'));
        toast.show();
    }
    
    // Search functionality
    $('.search-ops').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('.op-row').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
    
    // Toggle direction for phonetic text
    $('.toggle-direction').click(function() {
        $('.phonetic-text').each(function() {
            var currentDir = $(this).css('direction');
            var newDir = (currentDir === 'ltr') ? 'rtl' : 'ltr';
            $(this).css('direction', newDir);
        });
    });
    
    // Scroll to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $('#scrollToTop').fadeIn();
        } else {
            $('#scrollToTop').fadeOut();
        }
    });
    
    $('#scrollToTop').click(function() {
        $('html, body').animate({scrollTop: 0}, 'slow');
        return false;
    });
    
    // Print functionality
    $('#printResults').click(function() {
        window.print();
    });
});