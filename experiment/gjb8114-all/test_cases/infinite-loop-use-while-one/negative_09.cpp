class Worker {
public:
    int run(int limit) {
        int count = 0;
        for (; true; ) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
        {
            ++count;
            if (count >= limit) {
                break;
            }
        }
        return count;
    }
};

int main() {
    Worker worker;
    return worker.run(3) == 3 ? 0 : 1;
}
