int classify(int a, int b, int c, int d, int e, int f, int g, int h) {
    return a ? 1
         : b ? 2
         : c ? 3
         : d ? 4
         : e ? 5
         : f ? 6
         : g ? 7
         : h ? 8 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
         : 9;
}
