FROM php:7.4-apache

# Enable mod_rewrite
RUN a2enmod rewrite

# Copy PHP file
COPY index.php /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html

# Expose port 80
EXPOSE 80

# Apache will start automatically