enum class Mode { Idle, Active };

int main() {
    Mode mode = Mode::Active;
    switch (mode) { default: return static_cast<int>(mode); } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
}
