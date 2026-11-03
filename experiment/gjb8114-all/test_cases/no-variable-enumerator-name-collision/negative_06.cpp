enum Weekday { sunday, monday };

int main()
{
    if (int sunday = 1; sunday > 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
        return sunday;
    }
    Weekday day = monday;
    return static_cast<int>(day);
}
