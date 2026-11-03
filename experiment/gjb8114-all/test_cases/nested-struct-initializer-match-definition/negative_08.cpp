struct Spixel
{
    unsigned int colour;
    struct Scoords
    {
        unsigned int x;
        unsigned int y;
    } coords;
};

Spixel make_pixel()
{
    return {1, 2, 3}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-3]
}

int main(void)
{
    (void)make_pixel();
    return (0);
}
