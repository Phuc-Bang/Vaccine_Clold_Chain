'use client';

import { useEffect, useState } from 'react';
import { getTelemetry, type Telemetry } from '@/lib/api';
import { TemperatureChart } from './TemperatureChart';
import { StatusCard } from './StatusCard';
import { Thermometer, Droplets, Battery, Signal, ShieldCheck, AlertTriangle } from 'lucide-react';
import { formatTemp, cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export default function Dashboard() {
    const [data, setData] = useState<Telemetry[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const res = await getTelemetry();
            setData(res);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const latest = data[0];
    const hasData = !!latest;
    const isCritical = hasData && (latest.temperature > 8 || latest.temperature < 2);

    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900 pb-20 selection:bg-blue-100 selection:text-blue-900">
            {/* Background Decor - Subtle Grid Pattern */}
            <div className="fixed inset-0 pointer-events-none opacity-40"
                style={{ backgroundImage: 'radial-gradient(#CBD5E1 1px, transparent 1px)', backgroundSize: '32px 32px' }}>
            </div>

            <div className="max-w-7xl mx-auto space-y-8 relative z-10 p-6 sm:p-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-2">
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <div className="p-2.5 bg-blue-600 rounded-xl shadow-lg shadow-blue-200/50">
                                <ShieldCheck className="text-white" size={28} strokeWidth={2} />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold tracking-tight text-slate-900 leading-tight">Vaccine Cold Chain</h1>
                                <p className="text-sm font-medium text-slate-500">Giám sát kho lạnh thông minh</p>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <Badge variant="outline" className="pl-4 pr-5 py-2 rounded-full border-slate-200 bg-white shadow-sm gap-2.5 text-sm font-medium text-slate-600 hover:bg-white">
                            <div className="flex h-2.5 w-2.5 relative">
                                <span className={cn("animate-ping absolute inline-flex h-full w-full rounded-full opacity-75", hasData ? "bg-emerald-400" : "bg-amber-400")}></span>
                                <span className={cn("relative inline-flex rounded-full h-2.5 w-2.5", hasData ? "bg-emerald-500" : "bg-amber-500")}></span>
                            </div>
                            {hasData ? "Hệ thống trực tuyến" : "Đang kết nối..."}
                        </Badge>
                    </div>
                </div>

                <Separator className="bg-slate-200" />

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                    <StatusCard
                        title="Nhiệt Độ Kho"
                        value={hasData ? formatTemp(latest.temperature) : '--'}
                        icon={Thermometer}
                        status={isCritical ? 'critical' : 'normal'}
                        subtext="Ngưỡng: 2°C - 8°C"
                    />
                    <StatusCard
                        title="Độ Ẩm"
                        value={hasData ? latest.humidity?.toFixed(1) : '--'}
                        unit="%"
                        icon={Droplets}
                        subtext="Độ ẩm lý tưởng"
                    />
                    <StatusCard
                        title="Pin Thiết Bị"
                        value={hasData ? latest.battery_level : '--'}
                        unit="%"
                        icon={Battery}
                        status={hasData && latest.battery_level && latest.battery_level < 20 ? 'warning' : 'normal'}
                    />
                    <StatusCard
                        title="Tín Hiệu"
                        value={hasData ? latest.signal_strength : '--'}
                        unit="dBm"
                        icon={Signal}
                        subtext="Kết nối ổn định"
                    />
                </div>

                {/* Main Content Area */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Chart Section */}
                    <div className="lg:col-span-2">
                        <TemperatureChart data={data.length > 0 ? [...data].reverse() : []} />
                    </div>

                    {/* Side Panel: Alerts & Info */}
                    <div className="space-y-6">
                        {/* Alert Box */}
                        <Card className={cn("overflow-hidden border transition-all", isCritical ? "border-red-200 shadow-md shadow-red-100/50" : "border-slate-200 shadow-sm")}>
                            <CardHeader className={cn("border-b px-6 py-4", isCritical ? "bg-red-50/50 border-red-100" : "bg-white border-slate-100")}>
                                <div className="flex items-center gap-3">
                                    {isCritical ? <AlertTriangle size={20} className="text-red-600" /> : <ShieldCheck size={20} className="text-emerald-600" />}
                                    <CardTitle className={cn("text-lg", isCritical ? "text-red-800" : "text-slate-800")}>
                                        {isCritical ? "Cảnh Báo Hệ Thống" : "Trạng Thái An Toàn"}
                                    </CardTitle>
                                </div>
                            </CardHeader>

                            <CardContent className="p-6">
                                {isCritical ? (
                                    <div className="space-y-4">
                                        <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-100">
                                            <strong>⚠️ Nhiệt độ vượt ngưỡng an toàn!</strong>
                                            <p className="mt-1 text-red-600/90">Hệ thống phát hiện nhiệt độ kho lạnh vượt quá giới hạn cài đặt.</p>
                                        </div>
                                        <Button variant="destructive" className="w-full shadow-red-200">
                                            Xem chi tiết sự cố
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        <p className="text-slate-500 text-sm leading-relaxed">
                                            Hệ thống đang hoạt động ổn định trong các thông số cài đặt.
                                        </p>
                                        <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100 text-sm font-medium">
                                            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                                            Không có cảnh báo mới
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        {/* System Info */}
                        <Card className="border-slate-200 bg-slate-50/50">
                            <CardContent className="p-5">
                                <h3 className="font-semibold text-slate-900 mb-4 text-sm uppercase tracking-wide">Thông tin thiết bị</h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-slate-500">Gateway ID</span>
                                        <Badge variant="secondary" className="font-mono bg-white border-slate-200 text-slate-700 hover:bg-white">GW-VACCINE-01</Badge>
                                    </div>
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-slate-500">Phiên bản</span>
                                        <span className="font-medium text-slate-700">v1.2.4 (Stable)</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-slate-500">Thời gian chạy</span>
                                        <span className="text-emerald-600 font-medium">12 ngày, 4 giờ</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
