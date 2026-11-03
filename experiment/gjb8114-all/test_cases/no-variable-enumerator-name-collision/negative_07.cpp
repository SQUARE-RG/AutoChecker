enum State { idle, busy };

struct Worker {
    int idle; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
};

int main() {
    Worker w;
    w.idle = 1;
    State s = idle;
    (void)s;
    return 0;
}
