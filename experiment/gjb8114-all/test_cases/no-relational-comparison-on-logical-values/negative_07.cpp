struct FlagPair {
    bool result;
    FlagPair(bool left, bool right) : result(left > right) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
    }
};

int main() {
    FlagPair pair(true, false);
    return pair.result ? 0 : 1;
}
