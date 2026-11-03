typedef enum { RED, GREEN, BLUE } Color;

int main()
{
    Color color = RED;
    switch (color) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
    {
        case RED:
            break;
        case GREEN:
            break;
    }
    return 0;
}
