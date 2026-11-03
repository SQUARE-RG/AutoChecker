int g_max_connections = 64; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]

int main() {
    return g_max_connections;
}
