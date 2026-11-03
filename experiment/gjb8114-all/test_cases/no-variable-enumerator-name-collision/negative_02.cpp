enum Weekend { saturday, sunday };

int main()
{
    int total = 0;
    for (int sunday = 0; sunday < 3; ++sunday) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
        total += sunday;
    }
    return total;
}
