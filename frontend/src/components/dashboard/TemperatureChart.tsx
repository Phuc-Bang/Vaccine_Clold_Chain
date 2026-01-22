'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface DataPoint {
    timestamp: string;
    temperature: number;
    humidity: number;
}

interface Props {
    data: DataPoint[];
}

export function TemperatureChart({ data }: Props) {
    return (
        <Card className="w-full border-slate-200 shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-7">
                <div className="space-y-1">
                    <CardTitle className="text-xl font-bold text-slate-800">Biểu Đồ Nhiệt Độ</CardTitle>
                    <CardDescription>Giám sát trong 24 giờ qua</CardDescription>
                </div>
                <Badge variant="outline" className="flex items-center gap-2 px-3 py-1 text-sm border-slate-200 bg-slate-50 text-slate-600">
                    <div className="w-2 h-2 rounded-full bg-blue-500" /> Safe Range: 2-8°C
                </Badge>
            </CardHeader>

            <CardContent>
                <div className="h-[350px] w-full min-w-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data}>
                            <defs>
                                <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
                                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                            <XAxis
                                dataKey="timestamp"
                                tickFormatter={(str) => new Date(str).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                stroke="#64748B"
                                tick={{ fontSize: 12, fontWeight: 500 }}
                                axisLine={false}
                                tickLine={false}
                                dy={10}
                            />
                            <YAxis
                                domain={[0, 15]}
                                stroke="#64748B"
                                tick={{ fontSize: 12, fontWeight: 500 }}
                                axisLine={false}
                                tickLine={false}
                                dx={-10}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                    borderRadius: '8px',
                                    border: '1px solid #E2E8F0',
                                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                                }}
                                labelStyle={{ color: '#64748B', marginBottom: '4px' }}
                                itemStyle={{ color: '#1E293B', fontWeight: 600 }}
                                labelFormatter={(label) => new Date(label).toLocaleString()}
                            />
                            <Area
                                type="monotone"
                                dataKey="temperature"
                                stroke="#3B82F6"
                                strokeWidth={3}
                                fillOpacity={1}
                                fill="url(#colorTemp)"
                                animationDuration={1000}
                            />
                            {/* Safe Lines */}
                            <Area type="monotone" dataKey={() => 8} stroke="#22C55E" strokeDasharray="4 4" fill="transparent" strokeWidth={1} strokeOpacity={0.5} />
                            <Area type="monotone" dataKey={() => 2} stroke="#22C55E" strokeDasharray="4 4" fill="transparent" strokeWidth={1} strokeOpacity={0.5} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
