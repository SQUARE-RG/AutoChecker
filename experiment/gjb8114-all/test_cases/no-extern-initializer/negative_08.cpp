enum Color { RED, GREEN };

extern Color g_color = GREEN; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main()
{
    g_color = RED;
    return 0;
}
