struct POINTA
{
    unsigned int x;
    unsigned int y;
};

int main(void)
{
    unsigned int POINTA; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
    POINTA = 1;
    return static_cast<int>(POINTA);
}
