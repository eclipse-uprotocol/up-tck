; ModuleID = 'probe5.7dc120f2c13478db-cgu.0'
source_filename = "probe5.7dc120f2c13478db-cgu.0"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc"

; core::f64::<impl f64>::is_subnormal
; Function Attrs: inlinehint uwtable
define internal zeroext i1 @"_ZN4core3f6421_$LT$impl$u20$f64$GT$12is_subnormal17h72b364e3cdd93e64E"(double %self) unnamed_addr #0 {
start:
  %_2 = alloca i8, align 1
  %_4 = fcmp une double %self, %self
  br i1 %_4, label %bb1, label %bb2

bb2:                                              ; preds = %start
  %b = bitcast double %self to i64
  %_6 = and i64 %b, 4503599627370495
  %_7 = and i64 %b, 9218868437227405312
  %0 = icmp eq i64 %_6, 0
  br i1 %0, label %bb7, label %bb5

bb1:                                              ; preds = %start
  store i8 0, ptr %_2, align 1
  br label %bb3

bb7:                                              ; preds = %bb2
  switch i64 %_7, label %bb5 [
    i64 9218868437227405312, label %bb8
    i64 0, label %bb9
  ]

bb5:                                              ; preds = %bb7, %bb2
  %1 = icmp eq i64 %_7, 0
  br i1 %1, label %bb10, label %bb6

bb8:                                              ; preds = %bb7
  store i8 1, ptr %_2, align 1
  br label %bb4

bb9:                                              ; preds = %bb7
  store i8 2, ptr %_2, align 1
  br label %bb4

bb4:                                              ; preds = %bb6, %bb10, %bb9, %bb8
  br label %bb3

bb10:                                             ; preds = %bb5
  store i8 3, ptr %_2, align 1
  br label %bb4

bb6:                                              ; preds = %bb5
  store i8 4, ptr %_2, align 1
  br label %bb4

bb3:                                              ; preds = %bb1, %bb4
  %2 = load i8, ptr %_2, align 1, !range !2, !noundef !3
  %_3 = zext i8 %2 to i64
  %_0 = icmp eq i64 %_3, 3
  ret i1 %_0
}

; probe5::probe
; Function Attrs: uwtable
define void @_ZN6probe55probe17h8a24f7f3650db536E() unnamed_addr #1 {
start:
; call core::f64::<impl f64>::is_subnormal
  %_1 = call zeroext i1 @"_ZN4core3f6421_$LT$impl$u20$f64$GT$12is_subnormal17h72b364e3cdd93e64E"(double 1.000000e+00)
  ret void
}

attributes #0 = { inlinehint uwtable "target-cpu"="x86-64" "target-features"="+cx16,+sse3,+sahf" }
attributes #1 = { uwtable "target-cpu"="x86-64" "target-features"="+cx16,+sse3,+sahf" }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 8, !"PIC Level", i32 2}
!1 = !{!"rustc version 1.78.0 (9b00956e5 2024-04-29)"}
!2 = !{i8 0, i8 5}
!3 = !{}
